"""Load an English demo catalog without overwriting existing books or categories."""

from django.core.management.base import BaseCommand

from shop.models import Category, Product


CATEGORIES = {
    "Personal Development": "Practical books for habits, learning, and self-improvement.",
    "Children's Books": "Stories and picture books for young readers.",
    "Classics": "Enduring works of world literature.",
    "Science Fiction": "Speculative stories about science, technology, and the future.",
    "Fantasy": "Imaginary worlds, magic, and epic adventures.",
    "Romance": "Stories centered on love and relationships.",
    "Mystery and Thriller": "Detective stories, suspense, and psychological thrillers.",
    "Literary Fiction": "Character-driven contemporary and philosophical fiction.",
    "Historical Fiction": "Fiction set in the past.",
    "History and Science": "Accessible books about history, society, and science.",
    "Biography and Memoir": "Life stories and personal memoirs.",
    "Business and Finance": "Books about business, money, and personal finance.",
}

# product_id, title, author, genre, category, price in KZT, stock quantity
BOOKS = [
    ("P-1101", "The Hobbit", "J. R. R. Tolkien", "Fantasy", "Fantasy", 6200, 12),
    ("P-1102", "Pride and Prejudice", "Jane Austen", "Romance", "Romance", 4200, 9),
    ("P-1103", "The Silent Patient", "Alex Michaelides", "Psychological Thriller", "Mystery and Thriller", 5500, 11),
    ("P-1104", "The Thursday Murder Club", "Richard Osman", "Mystery", "Mystery and Thriller", 5800, 7),
    ("P-1105", "Dune", "Frank Herbert", "Science Fiction", "Science Fiction", 6800, 10),
    ("P-1106", "The Alchemist", "Paulo Coelho", "Philosophical Fiction", "Literary Fiction", 3900, 14),
    ("P-1107", "The Book Thief", "Markus Zusak", "Historical Fiction", "Historical Fiction", 5100, 6),
    ("P-1108", "Sapiens", "Yuval Noah Harari", "Popular Science", "History and Science", 7200, 8),
    ("P-1109", "Educated", "Tara Westover", "Memoir", "Biography and Memoir", 4900, 5),
    ("P-1110", "The Very Hungry Caterpillar", "Eric Carle", "Picture Book", "Children's Books", 2800, 20),
    ("P-1111", "The Midnight Library", "Matt Haig", "Contemporary Fiction", "Literary Fiction", 5300, 13),
    ("P-1112", "The Psychology of Money", "Morgan Housel", "Personal Finance", "Business and Finance", 6100, 9),
    ("P-1113", "The Fellowship of the Ring", "J. R. R. Tolkien", "Fantasy", "Fantasy", 6500, 8),
    ("P-1114", "Little Women", "Louisa May Alcott", "Classic Fiction", "Classics", 4600, 10),
    ("P-1115", "The Martian", "Andy Weir", "Science Fiction", "Science Fiction", 5900, 7),
]


class Command(BaseCommand):
    help = "Adds English demo categories and books without overwriting existing records"

    def handle(self, *args, **options):
        for name, description in CATEGORIES.items():
            Category.objects.get_or_create(
                category_name=name,
                defaults={"description": description},
            )

        added_books = 0
        for product_id, name, author, genre, category_name, price, stock in BOOKS:
            category = Category.objects.get(category_name=category_name)
            _, created = Product.objects.get_or_create(
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
            added_books += int(created)

        self.stdout.write(self.style.SUCCESS(
            f"Loaded {len(CATEGORIES)} demo categories and {added_books} new books."
        ))
