from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("shop", "0008_address_delivery_details")]

    operations = [
        migrations.AddField(
            model_name="address",
            name="within_city",
            field=models.BooleanField(default=True),
        ),
    ]
