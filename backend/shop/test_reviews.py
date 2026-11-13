"""Тесты отзывов, рейтинга и фильтров каталога по цене и рейтингу."""

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from rest_framework.test import APITestCase

from .models import Customer, Product, Review


class ReviewTests(APITestCase):
    def setUp(self):
        self.cheap = Product.objects.create(
            product_id="P-1001", product_name="Cheap", author="A", genre="X", price=2000, stock_quantity=5)
        self.mid = Product.objects.create(
            product_id="P-1002", product_name="Middle", author="B", genre="X", price=5000, stock_quantity=5)
        self.expensive = Product.objects.create(
            product_id="P-1003", product_name="Expensive", author="C", genre="X", price=9000, stock_quantity=5)

    def register(self, email="aruzhan@example.com", name="Aruzhan"):
        r = self.client.post("/api/register/", {
            "full_name": name, "email": email, "password": "StrongPass-2026"}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        return r.data["token"]

    def review(self, token, product_id, rating, comment=""):
        return self.client.post(
            f"/api/products/{product_id}/reviews/", {"rating": rating, "comment": comment},
            format="json", HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_logged_in_customer_adds_review_and_everyone_sees_it(self):
        token = self.register()
        r = self.review(token, "P-1002", 5, "Great book")
        self.assertEqual(r.status_code, 201, r.data)
        # отзыв видит любой посетитель, даже без входа
        r = self.client.get("/api/products/P-1002/reviews/")
        self.assertEqual(len(r.data), 1)
        self.assertEqual(r.data[0]["customer_name"], "Aruzhan")
        self.assertEqual(r.data[0]["comment"], "Great book")
        self.assertFalse(r.data[0]["is_mine"])  # гость — не автор
        r = self.client.get("/api/products/P-1002/reviews/", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertTrue(r.data[0]["is_mine"])
        self.assertNotIn("email", r.data[0])  # чужой email не показываем

    def test_review_needs_login(self):
        r = self.client.post("/api/products/P-1002/reviews/", {"rating": 5}, format="json")
        self.assertEqual(r.status_code, 401)
        # поддельный токен тоже не проходит
        r = self.review("fake-token", "P-1002", 5)
        self.assertEqual(r.status_code, 401)
        self.assertEqual(Review.objects.count(), 0)

    def test_rating_must_be_1_to_5(self):
        token = self.register()
        self.assertEqual(self.review(token, "P-1002", 0).status_code, 400)
        self.assertEqual(self.review(token, "P-1002", 6).status_code, 400)

    def test_second_review_updates_the_first(self):
        token = self.register()
        self.assertEqual(self.review(token, "P-1002", 2).status_code, 201)
        self.assertEqual(self.review(token, "P-1002", 4).status_code, 200)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.get().rating, 4)

    def test_database_blocks_duplicate_and_bad_rating(self):
        customer = Customer.objects.create(full_name="Dana", email="dana@example.com")
        Review.objects.create(customer=customer, product=self.mid, rating=5)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.create(customer=customer, product=self.mid, rating=3)  # UNIQUE
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.create(customer=customer, product=self.cheap, rating=9)  # CHECK

    def test_average_rating_in_catalog(self):
        self.review(self.register("a@example.com", "A"), "P-1002", 5)
        self.review(self.register("b@example.com", "B"), "P-1002", 4)
        book = self.client.get("/api/products/P-1002/").data
        self.assertEqual(book["avg_rating"], 4.5)
        self.assertEqual(book["review_count"], 2)
        no_reviews = self.client.get("/api/products/P-1001/").data
        self.assertIsNone(no_reviews["avg_rating"])
        self.assertEqual(no_reviews["review_count"], 0)

    def ids(self, url):
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200, r.data)
        return [p["product_id"] for p in r.data]

    def test_filter_by_price(self):
        self.assertEqual(self.ids("/api/products/?min_price=3000"), ["P-1002", "P-1003"])
        self.assertEqual(self.ids("/api/products/?max_price=5000"), ["P-1001", "P-1002"])
        self.assertEqual(self.ids("/api/products/?min_price=3000&max_price=6000"), ["P-1002"])
        self.assertEqual(self.client.get("/api/products/?min_price=abc").status_code, 400)

    def test_filter_and_sort_by_rating(self):
        self.review(self.register("a@example.com", "A"), "P-1003", 5)
        self.review(self.register("b@example.com", "B"), "P-1001", 3)
        self.assertEqual(self.ids("/api/products/?min_rating=4"), ["P-1003"])
        # лучшие сверху, книга без отзывов — в конце
        self.assertEqual(self.ids("/api/products/?ordering=-rating"), ["P-1003", "P-1001", "P-1002"])

    def test_sort_by_price(self):
        self.assertEqual(self.ids("/api/products/?ordering=-price"), ["P-1003", "P-1002", "P-1001"])
        self.assertEqual(self.ids("/api/products/?ordering=price"), ["P-1001", "P-1002", "P-1003"])
        self.assertEqual(self.client.get("/api/products/?ordering=bad").status_code, 400)

    def test_review_creates_customer_row_for_new_user(self):
        token = self.register("new@example.com", "New Reader")
        self.review(token, "P-1001", 4)
        self.assertTrue(Customer.objects.filter(email="new@example.com", full_name="New Reader").exists())
