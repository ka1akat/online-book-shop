from django.db import migrations, models


BOOK_LANGUAGES = {
    "P-1001": ["English"],
    "P-1002": ["English", "Russian"],
    "P-1003": ["Kazakh", "Russian"],
    "P-1004": ["English", "Russian"],
    "P-1005": ["English", "Russian"],
}


def set_demo_book_languages(apps, schema_editor):
    Product = apps.get_model("shop", "Product")
    for product_id, languages in BOOK_LANGUAGES.items():
        Product.objects.filter(pk=product_id).update(available_languages=languages)


class Migration(migrations.Migration):
    dependencies = [("shop", "0022_product_reading_details")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="available_languages",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.RunPython(set_demo_book_languages, migrations.RunPython.noop),
    ]
