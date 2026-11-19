"""Тесты листа ожидания (Notify me), уведомлений, страницы «Мои заказы» и избранного (Wishlist)."""

from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Category, Customer, Order, Product, StockRequest, WishlistItem
from .services import notify_waiting_customers


class ShopUserMixin:
    def setUp(self):
        self.category = Category.objects.create(category_name="Novels")
        self.sold_out = Product.objects.create(
            product_id="P-2001", product_name="Sold out", author="A", genre="X",
            category=self.category, price=3000, stock_quantity=0)
        self.in_stock = Product.objects.create(
            product_id="P-2002", product_name="In stock", author="B", genre="X",
            category=self.category, price=4000, stock_quantity=5)

    def register(self, email="karakat@example.com", name="Karakat"):
        r = self.client.post("/api/register/", {
            "full_name": name, "email": email, "password": "StrongPass-2026"}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        return r.data["token"]

    def auth(self, token):
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


class NotifyMeTests(ShopUserMixin, APITestCase):
    def test_guest_with_email_joins_waiting_list_once(self):
        r = self.client.post("/api/products/P-2001/notify/", {"email": "Guest@Example.com "}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        self.assertFalse(r.data["notified"])
        # FR-07 критерий 2: тот же покупатель + та же книга -> одна строка
        r = self.client.post("/api/products/P-2001/notify/", {"email": "guest@example.com"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(StockRequest.objects.count(), 1)
        self.assertEqual(StockRequest.objects.get().customer.email, "guest@example.com")

    def test_logged_in_customer_uses_account_email(self):
        token = self.register()
        r = self.client.post("/api/products/P-2001/notify/", {"email": "someone@else.kz"}, format="json",
                             **self.auth(token))
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(StockRequest.objects.get().customer.email, "karakat@example.com")

    def test_guest_without_email_gets_400(self):
        r = self.client.post("/api/products/P-2001/notify/", {}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(StockRequest.objects.count(), 0)

    def test_book_in_stock_cannot_be_waited_for(self):
        # FR-07 критерий 1: ждать можно только книгу, которой нет
        r = self.client.post("/api/products/P-2002/notify/", {"email": "a@b.kz"}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_unknown_book_404(self):
        r = self.client.post("/api/products/P-0000/notify/", {"email": "a@b.kz"}, format="json")
        self.assertEqual(r.status_code, 404)

    def test_customer_can_leave_waiting_list(self):
        token = self.register()
        self.client.post("/api/products/P-2001/notify/", {}, format="json", **self.auth(token))
        r = self.client.delete("/api/products/P-2001/notify/", **self.auth(token))
        self.assertEqual(r.status_code, 204)
        self.assertEqual(StockRequest.objects.count(), 0)
        # без входа удалить нельзя
        self.assertEqual(self.client.delete("/api/products/P-2001/notify/").status_code, 401)


class NotificationTests(ShopUserMixin, APITestCase):
    def wait_for_sold_out(self, token):
        r = self.client.post("/api/products/P-2001/notify/", {}, format="json", **self.auth(token))
        self.assertEqual(r.status_code, 201, r.data)

    def test_restock_marks_requests_notified(self):
        token = self.register()
        self.wait_for_sold_out(token)
        # пока книги нет — уведомлять нечего
        self.assertEqual(notify_waiting_customers("P-2001"), 0)
        Product.objects.filter(pk="P-2001").update(stock_quantity=3)
        # FR-07 критерий 4: книга вернулась -> notified = true
        self.assertEqual(notify_waiting_customers("P-2001"), 1)
        stock_request = StockRequest.objects.get()
        self.assertTrue(stock_request.notified)
        self.assertIsNotNone(stock_request.notified_at)
        # второй раз то же уведомление не отправляется
        self.assertEqual(notify_waiting_customers("P-2001"), 0)

    def test_restock_in_admin_notifies(self):
        token = self.register()
        self.wait_for_sold_out(token)
        admin_user = User.objects.create_superuser("warehouse_boss", "w@shop.kz", "pass-12345")
        self.client.force_login(admin_user)
        r = self.client.post("/admin/shop/product/P-2001/change/", {
            "product_id": "P-2001", "product_name": "Sold out", "author": "A", "description": "",
            "publication_year": "", "genre": "X", "category": self.category.pk,
            "price": "3000", "stock_quantity": "4",
        })
        self.assertEqual(r.status_code, 302, getattr(r, "context", None) and r.context["adminform"].form.errors)
        self.assertTrue(StockRequest.objects.get().notified)

    def test_customer_sees_and_reads_notifications(self):
        token = self.register()
        self.wait_for_sold_out(token)
        r = self.client.get("/api/notifications/", **self.auth(token))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)
        self.assertFalse(r.data[0]["notified"])  # ещё ждём

        Product.objects.filter(pk="P-2001").update(stock_quantity=2)
        notify_waiting_customers("P-2001")
        r = self.client.get("/api/notifications/", **self.auth(token))
        self.assertTrue(r.data[0]["notified"])
        self.assertTrue(r.data[0]["in_stock"])
        self.assertFalse(r.data[0]["is_read"])

        r = self.client.post("/api/notifications/read/", **self.auth(token))
        self.assertEqual(r.data["marked_read"], 1)
        r = self.client.get("/api/notifications/", **self.auth(token))
        self.assertTrue(r.data[0]["is_read"])

    def test_notifications_are_private(self):
        token = self.register()
        self.wait_for_sold_out(token)
        other = self.register("other@example.com", "Other")
        r = self.client.get("/api/notifications/", **self.auth(other))
        self.assertEqual(r.data, [])
        self.assertEqual(self.client.get("/api/notifications/").status_code, 401)

    def test_waiting_again_after_book_sold_out_again(self):
        token = self.register()
        self.wait_for_sold_out(token)
        Product.objects.filter(pk="P-2001").update(stock_quantity=1)
        notify_waiting_customers("P-2001")
        Product.objects.filter(pk="P-2001").update(stock_quantity=0)
        r = self.client.post("/api/products/P-2001/notify/", {}, format="json", **self.auth(token))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.data["notified"])
        self.assertEqual(StockRequest.objects.count(), 1)


class MyOrdersTests(ShopUserMixin, APITestCase):
    def make_order(self, email):
        customer, _ = Customer.objects.get_or_create(email=email, defaults={"full_name": email})
        return Order.objects.create(customer=customer, reserved_until=timezone.now() + timedelta(minutes=15))

    def test_customer_sees_only_own_orders_newest_first(self):
        token = self.register()
        first = self.make_order("karakat@example.com")
        second = self.make_order("karakat@example.com")
        self.make_order("stranger@example.com")
        r = self.client.get("/api/my-orders/", **self.auth(token))
        self.assertEqual(r.status_code, 200)
        self.assertEqual([o["order_id"] for o in r.data], [second.order_id, first.order_id])

    def test_my_orders_needs_login(self):
        self.assertEqual(self.client.get("/api/my-orders/").status_code, 401)
        self.assertEqual(self.client.get("/api/my-orders/", **self.auth("fake")).status_code, 401)


class WishlistTests(ShopUserMixin, APITestCase):
    def test_add_list_and_remove(self):
        token = self.register()
        r = self.client.post("/api/wishlist/", {"product_id": "P-2002"}, format="json", **self.auth(token))
        self.assertEqual(r.status_code, 201, r.data)
        r = self.client.post("/api/wishlist/", {"product_id": "P-2001"}, format="json", **self.auth(token))
        self.assertEqual(r.status_code, 201)
        # второй раз та же книга не дублируется
        r = self.client.post("/api/wishlist/", {"product_id": "P-2002"}, format="json", **self.auth(token))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(WishlistItem.objects.count(), 2)

        r = self.client.get("/api/wishlist/", **self.auth(token))
        self.assertEqual([p["product_id"] for p in r.data], ["P-2001", "P-2002"])  # последние сверху
        self.assertIn("avg_rating", r.data[0])

        r = self.client.delete("/api/wishlist/P-2001/", **self.auth(token))
        self.assertEqual(r.status_code, 204)
        r = self.client.get("/api/wishlist/", **self.auth(token))
        self.assertEqual([p["product_id"] for p in r.data], ["P-2002"])

    def test_wishlist_is_private_and_needs_login(self):
        token = self.register()
        self.client.post("/api/wishlist/", {"product_id": "P-2002"}, format="json", **self.auth(token))
        other = self.register("other@example.com", "Other")
        self.assertEqual(self.client.get("/api/wishlist/", **self.auth(other)).data, [])
        self.assertEqual(self.client.get("/api/wishlist/").status_code, 401)
        self.assertEqual(
            self.client.post("/api/wishlist/", {"product_id": "P-2002"}, format="json").status_code, 401)

    def test_unknown_book_404(self):
        token = self.register()
        r = self.client.post("/api/wishlist/", {"product_id": "P-0000"}, format="json", **self.auth(token))
        self.assertEqual(r.status_code, 404)
