"""
Команда `python manage.py seed_books` — заполняет таблицу PRODUCTS книгами из Task 9.
Можно запускать несколько раз: существующие книги просто обновятся.
"""

from django.core.management.base import BaseCommand

from shop.models import Product

BOOKS = [
    # product_id, название, автор, жанр, цена (KZT), на складе
    ("P-1001", "Atomic Habits", "James Clear", "Self-development", 6500, 0),
    ("P-1002", "The Little Prince", "Antoine de Saint-Exupery", "Fairy tale", 3000, 25),
    ("P-1003", "Abai Zholy", "Mukhtar Auezov", "Novel", 4500, 8),
    ("P-1004", "1984", "George Orwell", "Dystopia", 5000, 7),
    ("P-1005", "Harry Potter 1", "J. K. Rowling", "Fantasy", 7000, 15),
]


class Command(BaseCommand):
    help = "Добавляет 5 книг из Task 9 в таблицу products"

    def handle(self, *args, **options):
        for pid, name, author, genre, price, stock in BOOKS:
            Product.objects.update_or_create(
                product_id=pid,
                defaults={
                    "product_name": name, "author": author, "genre": genre,
                    "price": price, "stock_quantity": stock,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Готово: {len(BOOKS)} книг в таблице products"))
