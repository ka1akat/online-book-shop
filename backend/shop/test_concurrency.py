import threading
import time
import uuid
from unittest import skipUnless
from unittest.mock import patch

from django.db import connection, connections
from django.test import TransactionTestCase

from shop.models import Order, OrderItem, Payment, Product, StockLog
from shop.services import ShopError, create_order, pay_order

GOOD_CARD = "4111111111111111"


def slow_bank(card_number, amount):
    """Банк отвечает 0,5 с: так оба запроса гарантированно «пересекаются»."""
    time.sleep(0.5)
    return True, "TX-" + uuid.uuid4().hex[:10].upper()


def run_in_threads(funcs):
    """Запускает функции ОДНОВРЕМЕННО в разных потоках. Возвращает список результатов."""
    barrier = threading.Barrier(len(funcs))
    results = [None] * len(funcs)

    def worker(i, func):
        try:
            barrier.wait()  # все потоки стартуют одновременно
            results[i] = ("ok", func())
        except ShopError as e:
            results[i] = ("error", e.status_code)
        except Exception as e:
            results[i] = ("crash", repr(e))
        finally:
            connections.close_all()

    threads = [threading.Thread(target=worker, args=(i, f)) for i, f in enumerate(funcs)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


@skipUnless(connection.vendor == "postgresql", "Нужна PostgreSQL: SQLite не умеет блокировать строки")
class ConcurrencyTests(TransactionTestCase):
    def setUp(self):
        Product.objects.create(product_id="P-1001", product_name="1984", author="Orwell",
                               genre="novel", price=1000, stock_quantity=5)
        Product.objects.create(product_id="P-1002", product_name="Little Prince",
                               author="Saint-Exupery", genre="tale", price=800, stock_quantity=1)

    def test_double_click_pays_order_only_once(self):
        """Два одновременных нажатия «Оплатить» на один заказ: оплата должна пройти один раз."""
        order = create_order({"full_name": "A", "email": "a@test.kz", "phone": ""},
                             [{"product_id": "P-1001", "quantity": 1}])
        pay = lambda: pay_order(order.order_id, GOOD_CARD)
        with patch("shop.services.fake_bank", side_effect=slow_bank):
            results = run_in_threads([pay, pay])

        self.assertEqual(sorted(r[0] for r in results), ["error", "ok"], results)
        self.assertEqual(Product.objects.get(pk="P-1001").stock_quantity, 4)  # списано один раз
        self.assertEqual(Payment.objects.filter(order=order, status="success").count(), 1)
        self.assertEqual(StockLog.objects.count(), 1)
        self.assertEqual(Order.objects.get(pk=order.pk).status, "paid")

    def test_two_buyers_one_last_copy(self):
        """Два покупателя одновременно бронируют последнюю книгу: бронь получит только один."""
        def buy(email):
            return lambda: create_order({"full_name": email, "email": email, "phone": ""},
                                        [{"product_id": "P-1002", "quantity": 1}])

        results = run_in_threads([buy("a@test.kz"), buy("b@test.kz")])

        self.assertEqual(sorted(r[0] for r in results), ["error", "ok"], results)
        self.assertEqual([r[1] for r in results if r[0] == "error"], [409])
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.filter(product_id="P-1002").count(), 1)