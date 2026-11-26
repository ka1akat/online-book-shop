from django.db import migrations, models


BOOK_DETAILS = {
    "P-1001": {
        "description": "James Clear explains how small routines can build into lasting change. The book follows a practical four-step framework—make it obvious, attractive, easy, and satisfying—to help readers build helpful habits and reduce unwanted ones. It combines research from biology, psychology, and neuroscience with everyday examples and exercises for shaping routines and the environment around them.",
        "page_count": 320,
        "edition_info": "Avery hardcover edition",
    },
    "P-1002": {
        "description": "A pilot makes an emergency landing in the Sahara and meets a mysterious boy from a tiny asteroid. As the Little Prince tells the story of his travels and the people he met on other planets, the pilot learns about the prince's rose and his journey to Earth. Their friendship frames a fable about seeing beyond appearances, caring for others, and understanding what matters.",
        "page_count": 96,
        "edition_info": "Penguin Random House hardcover edition",
    },
    "P-1003": {
        "description": "This historical novel follows Abai from childhood into adulthood on the Kazakh steppe. Through his relationships with family, poets, and community leaders, the story depicts the traditions, conflicts, and social changes of nineteenth-century Kazakh society. The work is an epic published in multiple books and volumes; the total page count depends on the edition.",
        "page_count": None,
        "edition_info": "Four-part epic; page count varies by edition",
    },
    "P-1004": {
        "description": "Winston Smith works at the Ministry of Truth, where he alters old records to match the ruling Party's version of events. In a society shaped by surveillance, propaganda, and fear, he begins a private diary and forms a forbidden relationship with Julia. His search for truth and personal freedom brings him into conflict with the system that controls everyday life.",
        "page_count": 352,
        "edition_info": "Signet mass-market paperback edition",
    },
    "P-1005": {
        "description": "On his eleventh birthday, Harry Potter discovers that he is a wizard and leaves his unhappy home to study at Hogwarts. He makes friends with Ron and Hermione, learns about his parents, and encounters a mystery surrounding the Sorcerer's Stone. The first story follows Harry through his first year at the school as he and his friends try to uncover what is being hidden.",
        "page_count": 336,
        "edition_info": "Scholastic paperback edition (Sorcerer's Stone title)",
        "product_name": "Harry Potter and the Sorcerer's Stone",
    },
}


def update_demo_books(apps, schema_editor):
    Product = apps.get_model("shop", "Product")
    for product_id, details in BOOK_DETAILS.items():
        Product.objects.filter(pk=product_id).update(**details)


class Migration(migrations.Migration):
    dependencies = [("shop", "0021_remove_empty_uncategorized")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="page_count",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="edition_info",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.RunPython(update_demo_books, migrations.RunPython.noop),
    ]
