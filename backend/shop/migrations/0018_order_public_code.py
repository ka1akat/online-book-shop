import uuid

from django.db import migrations, models


def fill_codes(apps, schema_editor):
    # Старые заказы тоже получают свой секретный код (у каждого он разный)
    Order = apps.get_model("shop", "Order")
    for order in Order.objects.filter(public_code__isnull=True):
        order.public_code = uuid.uuid4()
        order.save(update_fields=["public_code"])


class Migration(migrations.Migration):
    dependencies = [("shop", "0017_notifications_and_wishlist")]

    operations = [
        # 1) поле сначала можно оставить пустым, потому что у старых заказов кода ещё нет
        migrations.AddField(
            model_name="order",
            name="public_code",
            field=models.UUIDField(null=True, editable=False),
        ),
        # 2) каждому старому заказу выдаём свой код
        migrations.RunPython(fill_codes, migrations.RunPython.noop),
        # 3) теперь код обязателен и уникален
        migrations.AlterField(
            model_name="order",
            name="public_code",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
