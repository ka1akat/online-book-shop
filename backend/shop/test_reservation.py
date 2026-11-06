from django.test import TestCase

from shop.models import Order, Payment, Product, StockLog
from shop.services import ShopError, create_order, pay_order

GOOD_CARD = "4111111111111111"


class ReservationExtraTests(TestCase):
    def setUp(self):
        Product.objects.create(product_id="P-1001", product_name="1984", author="Orwell",
                               genre="novel", price=1000, stock_quantity=5)
        Product.objects.create(product_id="P-1002", product_name="Little Prince",
                               author="Saint-Exupery", genre="tale", price=800, stock_quantity=3)
        self.customer = {"full_name": "Aigerim", "email": "a@test.kz", "phone": ""}

    def test_reservation_lasts_exactly_15_minutes(self):
        order = create_order(self.customer, [{"product_id": "P-1001", "quantity": 2}])
        delta = order.reserved_until - order.order_date
        self.assertAlmostEqual(delta.total_seconds(), 15 * 60, delta=5)

    def test_rollback_is_all_or_nothing(self):
        order = create_order(self.customer, [{"product_id": "P-1001", "quantity": 2},
                                             {"product_id": "P-1002", "quantity": 1}])
        Product.objects.filter(pk="P-1002").update(stock_quantity=0)  # вторая книга закончилась
        with self.assertRaises(ShopError):
            pay_order(order.order_id, GOOD_CARD)
        self.assertEqual(Product.objects.get(pk="P-1001").stock_quantity, 5)  # первая не списана
        self.assertEqual(Order.objects.get(pk=order.pk).status, Order.Status.RESERVED)
        self.assertFalse(Payment.objects.filter(status="success").exists())
        self.assertFalse(StockLog.objects.exists())

    def test_cannot_pay_twice(self):
        order = create_order(self.customer, [{"product_id": "P-1001", "quantity": 1}])
        pay_order(order.order_id, GOOD_CARD)
        with self.assertRaises(ShopError) as ctx:
            pay_order(order.order_id, GOOD_CARD)
        self.assertEqual(ctx.exception.status_code, 409)
        self.assertEqual(Product.objects.get(pk="P-1001").stock_quantity, 4)  # списано один раз