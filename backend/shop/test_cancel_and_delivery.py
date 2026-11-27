from datetime import timedelta
from decimal import Decimal

from django.test import SimpleTestCase, TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from shop.delivery import is_free_delivery
from shop.models import Address, Category, Customer, Order, OrderItem, Product
from shop.services import ShopError, available_quantity, pay_order

GOOD_CARD = "4111111111111111"
EMAIL = "buyer@test.kz"


# ---- Помощники. Если схема базы изменится, править нужно только их ----
def make_book(product_id="P-1001", stock=5, price=1000):
    category, _ = Category.objects.get_or_create(category_name="AUTOTEST CATEGORY")
    return Product.objects.create(
        product_id=product_id, product_name="Book " + product_id, author="Author",
        genre="genre", price=price, stock_quantity=stock, category=category,
    )


def make_order(book, quantity=1, status=Order.Status.RESERVED, email=EMAIL,
               minutes=15, within_city=True):
    customer, _ = Customer.objects.get_or_create(
        email=email.lower(), defaults={"full_name": "Buyer"}
    )
    address = Address.objects.create(
        customer=customer, city="Semey", full_address="Abay Street 10",
        within_city=within_city,
    )
    order = Order.objects.create(
        customer=customer, address=address, status=status,
        reserved_until=timezone.now() + timedelta(minutes=minutes),
    )
    OrderItem.objects.create(
        order=order, product=book, quantity=quantity, unit_price=book.price
    )
    return order


# ---- Правило порога (без базы данных) ----
class FreeDeliveryRuleTests(SimpleTestCase):
    def test_9999_is_not_free(self):
        self.assertFalse(is_free_delivery(Decimal("9999")))

    def test_exactly_10000_is_not_free(self):
        # «превышает» = строго больше, поэтому ровно 10 000 доставка платная
        self.assertFalse(is_free_delivery(Decimal("10000")))

    def test_10000_01_is_free(self):
        self.assertTrue(is_free_delivery(Decimal("10000.01")))


# ---- Доставка в реальном заказе ----
class OrderDeliveryFeeTests(TestCase):
    def test_order_over_10000_has_free_delivery(self):
        order = make_order(make_book(price=6000, stock=10), quantity=2)  # 12 000
        self.assertEqual(order.delivery_fee, 0)
        self.assertEqual(order.total, Decimal("12000"))

    def test_order_exactly_10000_pays_delivery(self):
        order = make_order(make_book(price=5000, stock=10), quantity=2)  # ровно 10 000
        fee = order.delivery_fee
        self.assertGreater(fee, 0)
        self.assertEqual(order.total, Decimal("10000") + fee)

    def test_small_order_pays_delivery(self):
        order = make_order(make_book(price=4000, stock=10), quantity=1)  # 4 000
        self.assertGreater(order.delivery_fee, 0)

    def test_big_order_is_free_even_outside_city(self):
        order = make_order(make_book(price=5000, stock=10), quantity=3, within_city=False)  # 15 000
        self.assertEqual(order.delivery_fee, 0)
        self.assertEqual(order.total, Decimal("15000"))


# ---- Отмена брони покупателем ----
class CancelOrderApiTests(APITestCase):
    def cancel(self, order, email=EMAIL):
        return self.client.post(
            f"/api/orders/{order.order_id}/cancel/", {"email": email}, format="json"
        )

    def test_cancel_frees_the_books(self):
        book = make_book(stock=5)
        order = make_order(book, quantity=3)
        self.assertEqual(available_quantity(book), 2)  # 3 книги в брони

        r = self.cancel(order)

        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["status"], "cancelled")
        book.refresh_from_db()
        self.assertEqual(book.stock_quantity, 5)       # склад не менялся
        self.assertEqual(available_quantity(book), 5)  # книги снова свободны

    def test_wrong_email_cannot_cancel(self):
        order = make_order(make_book())
        r = self.cancel(order, email="other@test.kz")
        self.assertEqual(r.status_code, 404)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.RESERVED)  # бронь на месте

    def test_unknown_order_404(self):
        r = self.client.post("/api/orders/999999/cancel/", {"email": EMAIL}, format="json")
        self.assertEqual(r.status_code, 404)

    def test_paid_order_cannot_be_cancelled(self):
        order = make_order(make_book(), status=Order.Status.PAID)
        r = self.cancel(order)
        self.assertEqual(r.status_code, 409)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)

    def test_cancel_twice_second_is_rejected(self):
        order = make_order(make_book())
        self.assertEqual(self.cancel(order).status_code, 200)
        self.assertEqual(self.cancel(order).status_code, 409)

    def test_email_is_required(self):
        order = make_order(make_book())
        r = self.client.post(f"/api/orders/{order.order_id}/cancel/", {}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_email_check_ignores_letter_case(self):
        order = make_order(make_book())
        self.assertEqual(self.cancel(order, email="BUYER@Test.KZ").status_code, 200)

    def test_cancelled_order_cannot_be_paid(self):
        order = make_order(make_book())
        self.cancel(order)
        with self.assertRaises(ShopError) as ctx:
            pay_order(order.order_id, GOOD_CARD)
        self.assertEqual(ctx.exception.status_code, 409)