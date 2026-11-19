import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shop", "0014_product_publication_year"),
    ]

    operations = [
        migrations.CreateModel(
            name="StoreReview",
            fields=[
                ("review_id", models.AutoField(primary_key=True, serialize=False)),
                ("rating", models.PositiveSmallIntegerField()),
                ("comment", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "customer",
                    models.ForeignKey(
                        db_column="customer_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="store_reviews",
                        to="shop.customer",
                    ),
                ),
            ],
            options={"db_table": "shop_store_reviews", "ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="storereview",
            constraint=models.CheckConstraint(
                condition=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name="store_rating_1_to_5",
            ),
        ),
        migrations.AddConstraint(
            model_name="storereview",
            constraint=models.UniqueConstraint(
                fields=("customer",), name="one_store_review_per_customer"
            ),
        ),
    ]
