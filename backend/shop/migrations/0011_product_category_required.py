import django.db.models.deletion
from django.db import migrations, models


def assign_category_to_uncategorized_books(apps, schema_editor):
    Category = apps.get_model("shop", "Category")
    Product = apps.get_model("shop", "Product")
    fallback, _ = Category.objects.get_or_create(
        category_name="Uncategorized",
        defaults={"description": "Books that have not yet been assigned a category."},
    )
    Product.objects.filter(category__isnull=True).update(category=fallback)


class Migration(migrations.Migration):
    dependencies = [("shop", "0010_reviews")]

    operations = [
        migrations.RunPython(
            assign_category_to_uncategorized_books,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.ForeignKey(
                db_column="category_id",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="products",
                to="shop.category",
            ),
        ),
    ]
