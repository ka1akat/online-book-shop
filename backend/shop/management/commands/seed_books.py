"""Load the original five demo books and their matching categories."""

from django.core.management.base import BaseCommand

from shop.models import Category, Product


# product_id, title, author, genre/category, price (KZT), stock quantity
BOOKS = [
    ("P-1001", "Atomic Habits", "James Clear", "Self-development", 6500, 0),
    ("P-1002", "The Little Prince", "Antoine de Saint-Exupery", "Fairy tale", 3000, 25),
    ("P-1003", "Abai Zholy", "Mukhtar Auezov", "Novel", 4500, 8),
    ("P-1004", "1984", "George Orwell", "Dystopia", 5000, 7),
    ("P-1005", "Harry Potter 1", "J. K. Rowling", "Fantasy", 7000, 15),
]


class Command(BaseCommand):
    help = "Loads the original five demo books and their categories"

    def handle(self, *args, **options):
        for product_id, name, author, genre, price, stock in BOOKS:
            category, _ = Category.objects.get_or_create(category_name=genre)
            Product.objects.update_or_create(
                product_id=product_id,
                defaults={
                    "product_name": name,
                    "author": author,
                    "genre": genre,
                    "category": category,
                    "price": price,
                    "stock_quantity": stock,
                },
            )

        self.stdout.write(self.style.SUCCESS("Loaded the original five demo books."))
