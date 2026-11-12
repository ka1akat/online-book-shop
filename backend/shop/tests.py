from datetime import timedelta
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Address, Category, Customer, Employee, Order, Payment, Product, StockLog
from .services import ShopError, refund_payment
GOOD_CARD = "4111 1111 1111 1111"
BAD_CARD = "4111 1111 1111 0000"  # банк отклоняет
TEST_ADDRESS = {
    "city": "Semey", "within_city": True, "full_address": "Abay Street, building 10",
}


class ShopFlowTests(APITestCase):
    def setUp(self):
        self.book = Product.objects.create(
            product_id="P-1004", product_name="1984", author="George Orwell",
            genre="Dystopia", price=5000, stock_quantity=2,
        )

    def make_order(self, quantity=1, email="aidar@example.com"):
        return self.client.post("/api/orders/", {
            "customer": {"full_name": "Aidar Nurlanov", "email": email, "phone": "+77011112233"},
            "address": TEST_ADDRESS,
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

    def test_delivery_fee_is_based_on_city_limits_not_city_name(self):
        for email, city, within_city, expected_fee in [
            ("semey-in@example.com", "Semey", True, 1000),
            ("semey-out@example.com", "Semey", False, 1500),
        ]:
            response = self.client.post("/api/orders/", {
                "customer": {"full_name": "Test", "email": email, "phone": ""},
                "address": {**TEST_ADDRESS, "city": city, "within_city": within_city},
                "items": [{"product_id": "P-1004", "quantity": 1}],
            }, format="json")
            self.assertEqual(response.status_code, 201, response.data)
            self.assertEqual(response.data["delivery_fee"], expected_fee)
            self.assertEqual(float(response.data["total"]), 5000 + expected_fee)

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

    def test_manager_can_see_low_stock(self):
        self.login_as("manager")
        self.assertEqual(self.client.get("/api/products/low-stock/").status_code, 200)

    def test_finance_cannot_see_low_stock(self):
        self.login_as("finance")
        self.assertEqual(self.client.get("/api/products/low-stock/").status_code, 403)

    def test_support_cannot_see_low_stock(self):
        self.login_as("support")
        self.assertEqual(self.client.get("/api/products/low-stock/").status_code, 403)

    def test_manager_is_read_only_in_admin(self):
        self.login_as("manager")
        self.assertEqual(self.client.get("/admin/shop/product/").status_code, 200)
        self.assertEqual(self.client.get("/admin/shop/product/add/").status_code, 403)

    def test_support_cannot_open_payments_in_admin(self):
        self.login_as("support")
        self.assertEqual(self.client.get("/admin/shop/payment/").status_code, 403)

    def test_warehouse_cannot_open_orders_in_admin(self):
        self.login_as("warehouse")
        self.assertEqual(self.client.get("/admin/shop/order/").status_code, 403)

    def test_warehouse_stock_edit_is_logged_with_login_and_employee(self):
        Product.objects.create(
            product_id="P-1004", product_name="1984", author="George Orwell",
            genre="Dystopia", price=5000, stock_quantity=2,
        )
        self.login_as("warehouse")
        r = self.client.post("/admin/shop/product/P-1004/change/", {
            "product_id": "P-1004", "product_name": "1984", "author": "George Orwell",
            "genre": "Dystopia", "price": "5000.00", "stock_quantity": 12,
        })
        self.assertEqual(r.status_code, 302)
        log = StockLog.objects.get()
        self.assertEqual((log.changed_by, log.change_amount, log.reason), ("warehouse", 10, "delivery"))
        self.assertEqual(log.employee.user.username, "warehouse")

    def test_role_fills_user_permissions(self):
        self.login_as("warehouse")
        user = get_user_model().objects.get(username="warehouse")
        self.assertTrue(user.user_permissions.filter(codename="change_product").exists())
        self.assertFalse(user.user_permissions.filter(codename="view_payment").exists())
    def test_customer_cannot_open_admin(self):
        user = get_user_model().objects.create_user("buyer@example.com", password="x")
        self.client.force_login(user)
        r = self.client.get("/admin/")
        self.assertEqual(r.status_code, 302)  # не сотрудник: отправляют на вход в админку


class CategoryAndAddressApiTests(APITestCase):
    def test_categories_and_category_product_filter(self):
        fiction = Category.objects.create(category_name="Test Fiction")
        poetry = Category.objects.create(category_name="Test Poetry")
        Product.objects.create(
            product_id="P-1001", product_name="Book A", author="Author A", genre="novel",
            category=fiction, price=1000, stock_quantity=2,
        )
        Product.objects.create(
            product_id="P-1002", product_name="Book B", author="Author B", genre="poem",
            category=poetry, price=1000, stock_quantity=2,
        )

        categories = self.client.get("/api/categories/")
        self.assertEqual(categories.status_code, 200)
        self.assertIn("Test Fiction", {c["category_name"] for c in categories.data})
        self.assertIn("Test Poetry", {c["category_name"] for c in categories.data})

        books = self.client.get(f"/api/products/?category_id={fiction.pk}")
        self.assertEqual([book["product_id"] for book in books.data], ["P-1001"])

    def test_customer_can_save_and_list_delivery_address(self):
        Customer.objects.create(full_name="Test Customer", email="address@example.com")
        payload = {
            "email": "address@example.com", "city": "Semey", "within_city": False,
            "full_address": "Abay Street 10", "entrance": "2", "apartment": "25",
            "intercom_code": "25B", "floor": "4", "is_default": True,
        }
        created = self.client.post("/api/addresses/", payload, format="json")
        self.assertEqual(created.status_code, 201, created.data)
        self.assertEqual(created.data["within_city"], False)

        listed = self.client.get("/api/addresses/?email=address@example.com")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.data[0]["full_address"], "Abay Street 10")
        self.assertEqual(listed.data[0]["intercom_code"], "25B")
        self.assertEqual(Address.objects.count(), 1)


class RegisterTests(APITestCase):
    url = "/api/register/"
    data = {
        "full_name": "Test User",
        "email": "Test@Example.com",
        "password": "BookShop-2026!",
    }

    def test_register_saves_user_with_hashed_password(self):
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, 201)
        user = get_user_model().objects.get(username="test@example.com")
        self.assertEqual(user.first_name, "Test User")
        self.assertNotEqual(user.password, self.data["password"])
        self.assertTrue(user.check_password(self.data["password"]))
        self.assertNotIn("password", response.data)

    def test_duplicate_email_is_rejected(self):
        self.client.post(self.url, self.data, format="json")
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_weak_password_is_rejected(self):
        response = self.client.post(
            self.url, {**self.data, "password": "123"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(get_user_model().objects.count(), 0)


class LoginTests(APITestCase):
    url = "/api/login/"

    def setUp(self):
        get_user_model().objects.create_user(
            username="test@example.com",
            email="test@example.com",
            password="BookShop-2026!",
            first_name="Test User",
        )

    def test_correct_password_logs_in(self):
        response = self.client.post(
            self.url,
            {"email": "Test@Example.com", "password": "BookShop-2026!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["full_name"], "Test User")
        self.assertNotIn("password", response.data)

    def test_wrong_password_is_rejected(self):
        response = self.client.post(
            self.url,
            {"email": "test@example.com", "password": "wrong-password"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
class RefundTests(APITestCase):
    def setUp(self):
        self.book = Product.objects.create(
            product_id="P-1004", product_name="1984", author="George Orwell",
            genre="Dystopia", price=5000, stock_quantity=2,
        )
        self.order_id = self.make_order()
        self.client.post(f"/api/orders/{self.order_id}/pay/", {"card_number": GOOD_CARD}, format="json")
        self.payment = Payment.objects.get(order_id=self.order_id, status="success")
        # после оплаты на складе 1 штука

    def make_order(self, email="aidar@example.com"):
        r = self.client.post("/api/orders/", {
            "customer": {"full_name": "Aidar Nurlanov", "email": email, "phone": "+77011112233"},
            "address": TEST_ADDRESS,
            "items": [{"product_id": "P-1004", "quantity": 1}],
        }, format="json")
        return r.data["order_id"]

    def login_as(self, role):
        user = get_user_model().objects.create_user(role, password="x", is_staff=True)
        Employee.objects.create(user=user, role=role)
        self.client.force_login(user)

    def refund_in_admin(self, action="refund_defective"):
        return self.client.post("/admin/shop/payment/", {
            "action": action, "_selected_action": [self.payment.pk], "index": 0,
        })

    def test_refund_of_paid_order_runs_whole_transaction(self):
        refund_payment(self.payment.pk, changed_by="finance")
        self.payment.refresh_from_db()
        self.book.refresh_from_db()
        self.assertEqual(self.payment.status, "refunded")
        self.assertEqual(Order.objects.get(pk=self.order_id).status, "cancelled")
        self.assertEqual(self.book.stock_quantity, 2)  # книга вернулась на склад
        log = StockLog.objects.get(reason="refund")
        self.assertEqual((log.change_amount, log.changed_by), (1, "finance"))

    def test_failed_payment_cannot_be_refunded(self):
        order_id = self.make_order(email="dana@example.com")
        self.client.post(f"/api/orders/{order_id}/pay/", {"card_number": BAD_CARD}, format="json")
        failed = Payment.objects.get(status="failed")
        with self.assertRaises(ShopError):
            refund_payment(failed.pk)
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock_quantity, 1)  # склад не тронут

    def test_cannot_refund_twice(self):
        refund_payment(self.payment.pk)
        with self.assertRaises(ShopError):
            refund_payment(self.payment.pk)
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock_quantity, 2)  # не 3: второй возврат не прошёл

    def test_refund_rolls_back_if_a_step_fails(self):
        with patch("shop.services.StockLog") as fake_log:
            fake_log.objects.create.side_effect = RuntimeError("boom")
            with self.assertRaises(RuntimeError):
                refund_payment(self.payment.pk)
        self.payment.refresh_from_db()
        self.book.refresh_from_db()
        self.assertEqual(self.payment.status, "success")  # ROLLBACK: ничего не сохранилось
        self.assertEqual(self.book.stock_quantity, 1)

    def test_refund_saves_reason_and_time(self):
        refund_payment(self.payment.pk, reason="changed_mind")
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.refund_reason, "changed_mind")
        self.assertIsNotNone(self.payment.refunded_at)

    def test_unknown_reason_is_rejected(self):
        with self.assertRaises(ShopError):
            refund_payment(self.payment.pk, reason="because")
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "success")

    def test_finance_can_refund_in_admin(self):
        self.login_as("finance")
        self.assertEqual(self.refund_in_admin().status_code, 302)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "refunded")
        self.assertEqual(self.payment.refund_reason, "defective")

    def test_warehouse_and_support_cannot_refund_in_admin(self):
        for role in ("warehouse", "support"):
            self.login_as(role)
            self.assertEqual(self.refund_in_admin().status_code, 403)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "success")
