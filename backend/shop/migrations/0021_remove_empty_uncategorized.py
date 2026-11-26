from django.db import migrations


def remove_empty_uncategorized(apps, schema_editor):
    """
    Категорию «Uncategorized» создала миграция 0011 как запасную для книг без категории.
    Теперь у каждой книги есть настоящая категория, и пустая «Uncategorized» только мешает
    в фильтрах каталога. Удаляем её, только если в ней нет ни одной книги.
    """
    Category = apps.get_model("shop", "Category")
    Category.objects.filter(category_name="Uncategorized", products__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [("shop", "0020_customer_favorite_categories")]

    operations = [migrations.RunPython(remove_empty_uncategorized, migrations.RunPython.noop)]
