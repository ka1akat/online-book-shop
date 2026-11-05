from datetime import timedelta

from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Customer, Order, Payment, Product, StockLog
from django.contrib.auth import get_user_model
from .models import Employee

GOOD_CARD = "4111 1111 1111 1111"
BAD_CARD = "4111 1111 1111 0000"  # банк отклоняет


class ShopFlowTests(APITestCase):
    def setUp(self):
        self.book = Product.objects.create(
            product_id="P-1004", product_name="1984", author="George Orwell",
            genre="Dystopia", price=5000, stock_quantity=2,
        )

    def make_order(self, quantity=1, email="aidar@example.com"):
        return self.client.post("/api/orders/", {
            "customer": {"full_name": "Aidar Nurlanov", "email": email, "phone": "+77011112233"},
            "items": [{"product_id": "P-1004", "quantity": quantity}],
        }, format="json")

    def test_order_reserves_but_does_not_reduce_stock(self):
        r = self.make_order()
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["status"], "reserved")
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock_quantity, 2)  # склад ещё не уменьшен
        products = self.client.get("/api/products/").data
        self.assertEqual(products[0]["available"], 1)  # но 1 книга забронирована

    def test_cannot_reserve_more_than_available(self):
        self.make_order(quantity=2)
        r = self.make_order(quantity=1, email="dana@example.com")
        self.assertEqual(r.status_code, 409)  # overselling не происходит

    def test_successful_payment_runs_whole_transaction(self):
        order_id = self.make_order().data["order_id"]
        r = self.client.post(f"/api/orders/{order_id}/pay/", {"card_number": GOOD_CARD}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["status"], "paid")
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock_quantity, 1)
        self.assertEqual(StockLog.objects.get().change_amount, -1)
        self.assertEqual(Payment.objects.get().status, "success")

    def test_failed_then_successful_payment(self):
        order_id = self.make_order().data["order_id"]
        r = self.client.post(f"/api/orders/{order_id}/pay/", {"card_number": BAD_CARD}, format="json")
        self.assertEqual(r.status_code, 402)
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock_quantity, 2)  # при ошибке склад не тронут
        self.client.post(f"/api/orders/{order_id}/pay/", {"card_number": GOOD_CARD}, format="json")
        statuses = list(Payment.objects.order_by("payment_id").values_list("status", flat=True))
        self.assertEqual(statuses, ["failed", "success"])  # 1 заказ — 2 оплаты (1:M)

    def test_expired_reservation_cannot_be_paid(self):
        order_id = self.make_order().data["order_id"]
        Order.objects.filter(pk=order_id).update(reserved_until=timezone.now() - timedelta(minutes=1))
        r = self.client.post(f"/api/orders/{order_id}/pay/", {"card_number": GOOD_CARD}, format="json")
        self.assertEqual(r.status_code, 409)
        self.assertEqual(Order.objects.get(pk=order_id).status, "cancelled")

    def test_stock_cannot_be_negative(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Product.objects.filter(pk="P-1004").update(stock_quantity=-1)  # CHECK >= 0

    def test_cannot_delete_customer_with_orders(self):
        self.make_order()
        with self.assertRaises(ProtectedError):  # ON DELETE RESTRICT
            Customer.objects.get().delete()
    
   
class RoleAccessTests(APITestCase):
    def login_as(self, role):
        user = get_user_model().objects.create_user(role, password="x", is_staff=True)
        Employee.objects.create(user=user, role=role)
        self.client.force_login(user)

    def test_anonymous_cannot_see_low_stock(self):
        self.assertEqual(self.client.get("/api/products/low-stock/").status_code, 403)

    def test_warehouse_can_see_low_stock(self):
        self.login_as("warehouse")
        self.assertEqual(self.client.get("/api/products/low-stock/").status_code, 200)

    def test_finance_cannot_see_low_stock(self):
        self.login_as("finance")
        self.assertEqual(self.client.get("/api/products/low-stock/").status_code, 403)
