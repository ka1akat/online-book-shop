"""Load the demo catalog (categories + books) from shop/catalog_data.py.

    python manage.py seed_books                 # create or reset every demo book (local database)
    python manage.py seed_books --only-missing  # add only books that are not in the database yet
                                                # (build.sh on Render: keeps stock and prices)
"""

from django.core.management.base import BaseCommand

from shop.catalog_data import BOOKS, CATEGORIES, product_fields
from shop.models import Category, Product


class Command(BaseCommand):
    help = "Loads the demo categories and books (shop/catalog_data.py)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--only-missing", action="store_true",
            help="Only add categories and books that do not exist yet; never change existing ones.",
        )

    def handle(self, *args, only_missing=False, **options):
        categories = {}
        for name, description in CATEGORIES.items():
            category, created = Category.objects.get_or_create(
                category_name=name, defaults={"description": description}
            )
            if not created and not category.description:
                category.description = description
                category.save(update_fields=["description"])
            categories[name] = category

        added = 0
        for book in BOOKS:
            fields = product_fields(book, categories[book["category"]])
            if only_missing:
                _, created = Product.objects.get_or_create(product_id=book["product_id"], defaults=fields)
            else:
                _, created = Product.objects.update_or_create(product_id=book["product_id"], defaults=fields)
            added += created

        mode = "missing" if only_missing else "all"
        self.stdout.write(self.style.SUCCESS(
            f"Demo catalog ({mode}): {len(CATEGORIES)} categories, {len(BOOKS)} books, {added} new."
        ))
