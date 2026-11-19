from django.db import migrations, models


DESCRIPTIONS = {
    "P-1001": "A practical guide to building good habits and breaking bad ones through small, lasting changes.",
    "P-1002": "A thoughtful story about a young prince, his travels, and the meaning of friendship.",
    "P-1003": "A landmark Kazakh novel tracing Abai's life and the changing world around him.",
    "P-1004": "A dystopian classic about Winston Smith and life under a government that watches everyone.",
    "P-1005": "The first Harry Potter adventure begins when a young wizard discovers a hidden world of magic.",
}


def fill_existing_book_descriptions(apps, schema_editor):
    Product = apps.get_model("shop", "Product")
    for product_id, description in DESCRIPTIONS.items():
        Product.objects.filter(pk=product_id, description="").update(description=description)


class Migration(migrations.Migration):
    dependencies = [("shop", "0012_address_is_saved")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.RunPython(fill_existing_book_descriptions, migrations.RunPython.noop),
    ]
