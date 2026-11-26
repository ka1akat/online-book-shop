"""Тесты: рейтинг книг (top rating), письмо «книга снова в наличии», любимые категории и подборка «For you»."""

from datetime import timedelta
from unittest import mock

from django.core import mail
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Category, Customer, Order, OrderItem, Product, Review, StockRequest, WishlistItem
from .services import notify_waiting_customers


class ShopData(APITestCase):
    def setUp(self):
        self.novels = Category.objects.create(category_name="Novels")
        self.kids = Category.objects.create(category_name="Kids")
        self.fantasy = Category.objects.create(category_name="Fantasy")
        self.books = {}
        for pid, name, cat, stock in [
            ("P-3001", "Novel A", self.novels, 5), ("P-3002", "Novel B", self.novels, 5),
            ("P-3003", "Novel C", self.novels, 0), ("P-3004", "Kids A", self.kids, 5),
            ("P-3005", "Kids B", self.kids, 5), ("P-3006", "Fantasy A", self.fantasy, 5),
        ]:
            self.books[pid] = Product.objects.create(
                product_id=pid, product_name=name, author="Author", genre="x",
                category=cat, price=2000, stock_quantity=stock)
        self.reviewers = [
            Customer.objects.create(full_name=f"R{i}", email=f"r{i}@example.com") for i in range(3)
        ]

    def rate(self, pid, *ratings):
        for customer, rating in zip(self.reviewers, ratings):
            Review.objects.create(product=self.books[pid], customer=customer, rating=rating)

    def register(self, email="karakat@example.com"):
        r = self.client.post("/api/register/", {
            "full_name": "Karakat", "email": email, "password": "StrongPass-2026"}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        return {"HTTP_AUTHORIZATION": f"Bearer {r.data['token']}"}


class TopRatedTests(ShopData):
    def test_ranking_order_and_only_reviewed_books(self):
        self.rate("P-3001", 4, 4)        # 4.0, 2 отзыва
        self.rate("P-3004", 5)           # 5.0
        self.rate("P-3006", 4, 4, 4)     # 4.0, 3 отзыва -> выше P-3001
        r = self.client.get("/api/products/top-rated/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual([b["product_id"] for b in r.data], ["P-3004", "P-3006", "P-3001"])
        self.assertEqual(r.data[0]["avg_rating"], 5.0)

    def test_limit_and_category(self):
        self.rate("P-3001", 3)
        self.rate("P-3002", 5)
        self.rate("P-3004", 4)
        r = self.client.get("/api/products/top-rated/?limit=1")
        self.assertEqual([b["product_id"] for b in r.data], ["P-3002"])
        r = self.client.get(f"/api/products/top-rated/?category_id={self.kids.pk}")
        self.assertEqual([b["product_id"] for b in r.data], ["P-3004"])

    def test_empty_when_no_reviews(self):
        self.assertEqual(self.client.get("/api/products/top-rated/").data, [])

    def test_not_treated_as_product_id(self):
        # адрес top-rated/ не должен попадать в «книгу с id top-rated»
        self.assertEqual(self.client.get("/api/products/top-rated/").status_code, 200)


@override_settings(FRONTEND_URL="https://shop.example.com")
class BackInStockEmailTests(ShopData):
    def test_email_sent_to_each_waiting_customer(self):
        self.client.post("/api/products/P-3003/notify/", {"email": "guest@example.com"}, format="json")
        auth = self.register()
        self.client.post("/api/products/P-3003/notify/", {}, format="json", **auth)
        Product.objects.filter(pk="P-3003").update(stock_quantity=2)

        self.assertEqual(notify_waiting_customers("P-3003"), 2)
        self.assertEqual(sorted(m.to[0] for m in mail.outbox), ["guest@example.com", "karakat@example.com"])
        message = mail.outbox[0]
        self.assertIn("Novel C", message.subject)
        self.assertIn("https://shop.example.com/books/P-3003", message.body)
        self.assertIn("text/html", [mimetype for _, mimetype in message.alternatives])
        # второй вызов — писем больше нет: всем уже сообщили
        notify_waiting_customers("P-3003")
        self.assertEqual(len(mail.outbox), 2)

    def test_no_email_while_still_out_of_stock(self):
        self.client.post("/api/products/P-3003/notify/", {"email": "guest@example.com"}, format="json")
        notify_waiting_customers("P-3003")
        self.assertEqual(mail.outbox, [])

    def test_mail_failure_does_not_break_restock(self):
        self.client.post("/api/products/P-3003/notify/", {"email": "guest@example.com"}, format="json")
        Product.objects.filter(pk="P-3003").update(stock_quantity=2)
        with mock.patch("django.core.mail.EmailMultiAlternatives.send", side_effect=OSError("smtp down")):
            self.assertEqual(notify_waiting_customers("P-3003"), 1)
        self.assertTrue(StockRequest.objects.get().notified)  # уведомление на сайте всё равно есть

    @override_settings(EMAIL_BACKEND="shop.emails.BrevoEmailBackend", BREVO_API_KEY="test-key",
                       DEFAULT_FROM_EMAIL="Online Book Shop <shop@example.com>")
    def test_brevo_backend_builds_api_request(self):
        self.client.post("/api/products/P-3003/notify/", {"email": "guest@example.com"}, format="json")
        Product.objects.filter(pk="P-3003").update(stock_quantity=2)
        with mock.patch("shop.emails.urllib.request.urlopen") as urlopen:
            urlopen.return_value.__enter__.return_value.status = 201
            notify_waiting_customers("P-3003")
        request = urlopen.call_args[0][0]
        self.assertEqual(request.full_url, "https://api.brevo.com/v3/smtp/email")
        self.assertEqual(request.get_header("Api-key"), "test-key")
        import json
        body = json.loads(request.data)
        self.assertEqual(body["sender"], {"name": "Online Book Shop", "email": "shop@example.com"})
        self.assertEqual(body["to"], [{"email": "guest@example.com"}])
        self.assertIn("htmlContent", body)


class SimilarBooksTests(ShopData):
    def test_same_category_best_first_without_itself(self):
        self.rate("P-3002", 5)
        r = self.client.get("/api/products/P-3001/similar/?limit=2")
        self.assertEqual(r.status_code, 200)
        self.assertEqual([b["product_id"] for b in r.data], ["P-3002", "P-3003"])

    def test_filled_from_other_categories(self):
        r = self.client.get("/api/products/P-3006/similar/?limit=3")
        ids = [b["product_id"] for b in r.data]
        self.assertEqual(len(ids), 3)
        self.assertNotIn("P-3006", ids)

    def test_unknown_book(self):
        self.assertEqual(self.client.get("/api/products/P-0000/similar/").status_code, 404)


class PreferencesAndRecommendationsTests(ShopData):
    def test_save_and_read_favourite_categories(self):
        auth = self.register()
        r = self.client.put("/api/preferences/", {"category_ids": [self.kids.pk, self.fantasy.pk]},
                            format="json", **auth)
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["category_ids"], sorted([self.kids.pk, self.fantasy.pk]))
        r = self.client.get("/api/preferences/", **auth)
        self.assertEqual(r.data["category_ids"], sorted([self.kids.pk, self.fantasy.pk]))
        # пустой список — сбросить
        r = self.client.put("/api/preferences/", {"category_ids": []}, format="json", **auth)
        self.assertEqual(r.data["category_ids"], [])

    def test_unknown_category_and_login(self):
        auth = self.register()
        r = self.client.put("/api/preferences/", {"category_ids": [999]}, format="json", **auth)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.client.get("/api/preferences/").status_code, 401)
        self.assertEqual(self.client.get("/api/recommendations/").status_code, 401)

    def test_recommendations_from_favourites(self):
        auth = self.register()
        self.rate("P-3005", 5)
        self.client.put("/api/preferences/", {"category_ids": [self.kids.pk]}, format="json", **auth)
        r = self.client.get("/api/recommendations/", **auth)
        self.assertEqual(r.data["based_on"], "favorites")
        self.assertEqual(r.data["categories"], ["Kids"])
        self.assertEqual([b["product_id"] for b in r.data["books"]], ["P-3005", "P-3004"])

    def test_recommendations_from_activity_skip_wishlist(self):
        auth = self.register()
        self.client.post("/api/wishlist/", {"product_id": "P-3006"}, format="json", **auth)
        r = self.client.get("/api/recommendations/", **auth)
        self.assertEqual(r.data["based_on"], "activity")
        self.assertEqual(r.data["categories"], ["Fantasy"])
        self.assertEqual(r.data["books"], [])  # единственная книга Fantasy уже в избранном

    def test_bought_books_not_recommended(self):
        auth = self.register()
        customer, _ = Customer.objects.get_or_create(email="karakat@example.com", defaults={"full_name": "Karakat"})
        order = Order.objects.create(customer=customer, status="paid",
                                     reserved_until=timezone.now() + timedelta(minutes=15))
        OrderItem.objects.create(order=order, product=self.books["P-3001"], quantity=1, unit_price=2000)
        r = self.client.get("/api/recommendations/", **auth)
        self.assertEqual(r.data["based_on"], "activity")
        ids = [b["product_id"] for b in r.data["books"]]
        self.assertNotIn("P-3001", ids)
        self.assertEqual(sorted(ids), ["P-3002", "P-3003"])

    def test_new_customer_gets_top_rated(self):
        auth = self.register()
        self.rate("P-3004", 5)
        r = self.client.get("/api/recommendations/", **auth)
        self.assertEqual(r.data["based_on"], "top_rated")
        self.assertEqual(r.data["books"][0]["product_id"], "P-3004")
