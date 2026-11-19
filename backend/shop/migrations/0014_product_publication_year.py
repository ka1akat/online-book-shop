from django.db import migrations, models


BOOK_DETAILS = {
    "P-1001": (2018, "James Clear explains how small routines can build into lasting change. The book offers practical methods for creating helpful habits, changing your environment, and making progress easier to repeat."),
    "P-1002": (1943, "After meeting a young prince in the desert, a stranded pilot hears about the prince's travels between planets. Their conversations explore friendship, responsibility, and how people learn to value one another."),
    "P-1003": (1942, "Mukhtar Auezov's novel follows the poet and thinker Abai as he grows up on the Kazakh steppe. Through his life, the story portrays the customs, conflicts, and social changes of nineteenth-century Kazakh society."),
    "P-1004": (1949, "Winston Smith lives in a state where the government monitors its citizens and rewrites the past. His quiet search for truth and personal freedom becomes a dangerous challenge to the ruling system."),
    "P-1005": (1997, "On his eleventh birthday, Harry Potter learns that he is a wizard and begins life at Hogwarts. With new friends, he discovers the history of his family and a mystery connected to the school."),
}


def fill_book_details(apps, schema_editor):
    Product = apps.get_model("shop", "Product")
    for product_id, (year, description) in BOOK_DETAILS.items():
        Product.objects.filter(pk=product_id).update(
            publication_year=year,
            description=description,
        )


class Migration(migrations.Migration):
    dependencies = [("shop", "0013_product_description")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="publication_year",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.RunPython(fill_book_details, migrations.RunPython.noop),
    ]
