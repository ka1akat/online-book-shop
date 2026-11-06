from django.apps import apps
from django.db import IntegrityError, connection, transaction
from django.test import TestCase

from shop.models import Customer, Product


class PrimaryKeyTests(TestCase):
    def test_every_table_has_not_null_unique_pk(self):
        for model in apps.get_app_config("shop").get_models():
            pk = model._meta.pk
            with self.subTest(table=model._meta.db_table):
                self.assertTrue(pk.primary_key)
                self.assertFalse(pk.null)    # NOT NULL
                self.assertTrue(pk.unique)   # UNIQUE

    def test_null_pk_rejected_by_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            with connection.cursor() as cur:
                cur.execute(
                    "INSERT INTO products (product_id, product_name, author, genre, "
                    "price, stock_quantity, last_updated) "
                    "VALUES (NULL, 'T', 'A', 'g', 10, 1, '2026-01-01')"
                )

    def test_duplicate_product_pk_rejected(self):
        Product.objects.create(product_id="P-1001", product_name="A", author="X",
                               genre="g", price=10, stock_quantity=1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Product.objects.create(product_id="P-1001", product_name="B", author="Y",
                                   genre="g", price=10, stock_quantity=1)

    def test_duplicate_customer_pk_rejected(self):
        c = Customer.objects.create(full_name="A", email="a@test.kz")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Customer(customer_id=c.customer_id, full_name="B",
                     email="b@test.kz").save(force_insert=True)