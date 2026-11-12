from django.db import migrations, models


def copy_legacy_address(apps, schema_editor):
    Address = apps.get_model("shop", "Address")
    for address in Address.objects.filter(full_address="").iterator():
        address.full_address = f"{address.street} {address.building}".strip()
        address.save(update_fields=["full_address"])


class Migration(migrations.Migration):
    dependencies = [("shop", "0007_catalog_categories")]

    operations = [
        migrations.AddField(
            model_name="address",
            name="full_address",
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name="address",
            name="entrance",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="address",
            name="floor",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="address",
            name="intercom_code",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.RunPython(copy_legacy_address, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="address",
            name="street",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
        migrations.AlterField(
            model_name="address",
            name="building",
            field=models.CharField(blank=True, default="", max_length=30),
        ),
    ]
