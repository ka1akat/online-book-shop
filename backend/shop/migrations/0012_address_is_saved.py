from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("shop", "0011_product_category_required")]

    operations = [
        migrations.AddField(
            model_name="address",
            name="is_saved",
            field=models.BooleanField(default=True),
        ),
    ]
