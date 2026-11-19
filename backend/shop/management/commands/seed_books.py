"""Load the original five demo books and their matching categories."""

from django.core.management.base import BaseCommand

from shop.models import Category, Product


# product_id, title, author, genre, category, price (KZT), stock quantity
BOOKS = [
    ("P-1001", "Atomic Habits", "James Clear", "Self-development", "Personal Development", 6500, 0),
    ("P-1002", "The Little Prince", "Antoine de Saint-Exupery", "Fairy tale", "Children's Books", 3000, 25),
    ("P-1003", "Abai Zholy", "Mukhtar Auezov", "Novel", "Literature", 4500, 8),
    ("P-1004", "1984", "George Orwell", "Dystopia", "Fiction", 5000, 7),
    ("P-1005", "Harry Potter 1", "J. K. Rowling", "Fantasy", "Fantasy", 7000, 15),
]

DESCRIPTIONS = {
    "P-1001": "James Clear explains how small routines can build into lasting change. The book offers practical methods for creating helpful habits, changing your environment, and making progress easier to repeat.",
    "P-1002": "After meeting a young prince in the desert, a stranded pilot hears about the prince's travels between planets. Their conversations explore friendship, responsibility, and how people learn to value one another.",
    "P-1003": "Mukhtar Auezov's novel follows the poet and thinker Abai as he grows up on the Kazakh steppe. Through his life, the story portrays the customs, conflicts, and social changes of nineteenth-century Kazakh society.",
    "P-1004": "Winston Smith lives in a state where the government monitors its citizens and rewrites the past. His quiet search for truth and personal freedom becomes a dangerous challenge to the ruling system.",
    "P-1005": "On his eleventh birthday, Harry Potter learns that he is a wizard and begins life at Hogwarts. With new friends, he discovers the history of his family and a mystery connected to the school.",
}

PUBLICATION_YEARS = {"P-1001": 2018, "P-1002": 1943, "P-1003": 1942, "P-1004": 1949, "P-1005": 1997}


class Command(BaseCommand):
    help = "Loads the original five demo books and their categories"

    def handle(self, *args, **options):
        for product_id, name, author, genre, category_name, price, stock in BOOKS:
            category, _ = Category.objects.get_or_create(category_name=category_name)
            Product.objects.update_or_create(
                product_id=product_id,
                defaults={
                    "product_name": name,
                    "author": author,
                    "description": DESCRIPTIONS[product_id],
                    "publication_year": PUBLICATION_YEARS[product_id],
                    "genre": genre,
                    "category": category,
                    "price": price,
                    "stock_quantity": stock,
                },
            )

        self.stdout.write(self.style.SUCCESS("Loaded the original five demo books."))
