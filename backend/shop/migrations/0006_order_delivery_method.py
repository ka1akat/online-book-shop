from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("shop", "0005_payment_refund_reason_payment_refunded_at_and_more")]

    operations = [
        migrations.AddField(
            model_name="order",
            name="delivery_method",
            field=models.CharField(
                choices=[("delivery", "Delivery")],
                default="delivery",
                max_length=10,
            ),
        ),
    ]
