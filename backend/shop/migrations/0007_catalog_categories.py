from django.db import migrations


def regroup_seed_categories(apps, schema_editor):
    Category = apps.get_model("shop", "Category")
    Product = apps.get_model("shop", "Product")
    groups = {
        "Self-development": "Personal Development",
        "Fairy tale": "Children's Books",
        "Novel": "Literature",
        "Dystopia": "Fiction",
    }
    for genre, category_name in groups.items():
        category, _ = Category.objects.get_or_create(category_name=category_name)
        Product.objects.filter(genre=genre).update(category=category)
    Category.objects.filter(category_name__in=groups, products__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [("shop", "0006_order_delivery_method")]

    operations = [migrations.RunPython(regroup_seed_categories, migrations.RunPython.noop)]
