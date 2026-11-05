from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def copy_employee_details(apps, schema_editor):
    Employee = apps.get_model("shop", "Employee")
    for employee in Employee.objects.select_related("user"):
        user = employee.user
        employee.login = user.username
        employee.full_name = user.get_full_name() or user.username
        employee.password_hash = user.password
        employee.is_active = user.is_active
        employee.save(update_fields=["login", "full_name", "password_hash", "is_active"])


def link_existing_genres(apps, schema_editor):
    Product = apps.get_model("shop", "Product")
    Category = apps.get_model("shop", "Category")
    for genre in Product.objects.values_list("genre", flat=True).distinct():
        category, _ = Category.objects.get_or_create(category_name=genre)
        Product.objects.filter(genre=genre).update(category_id=category.pk)


class Migration(migrations.Migration):
    dependencies = [("shop", "0003_alter_employee_role"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(name="Address", fields=[
            ("address_id", models.AutoField(primary_key=True, serialize=False)),
            ("city", models.CharField(max_length=100)), ("street", models.CharField(max_length=150)),
            ("building", models.CharField(max_length=30)), ("apartment", models.CharField(blank=True, max_length=30)),
            ("is_default", models.BooleanField(default=False)),
            ("customer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="addresses", to="shop.customer")),
        ], options={"db_table": "addresses"}),
        migrations.CreateModel(name="Category", fields=[
            ("category_id", models.AutoField(primary_key=True, serialize=False)),
            ("category_name", models.CharField(max_length=50, unique=True)), ("description", models.TextField(blank=True)),
        ], options={"db_table": "categories"}),
        migrations.AddField(model_name="employee", name="login", field=models.CharField(blank=True, max_length=150, null=True, unique=True)),
        migrations.AddField(model_name="employee", name="full_name", field=models.CharField(blank=True, max_length=150)),
        migrations.AddField(model_name="employee", name="password_hash", field=models.CharField(blank=True, max_length=128)),
        migrations.AddField(model_name="employee", name="is_active", field=models.BooleanField(default=True)),
        migrations.RenameField(model_name="employee", old_name="id", new_name="employee_id"),
        migrations.RunPython(copy_employee_details, migrations.RunPython.noop),
        migrations.AddField(model_name="product", name="category", field=models.ForeignKey(blank=True, db_column="category_id", null=True, on_delete=django.db.models.deletion.PROTECT, related_name="products", to="shop.category")),
        migrations.RunPython(link_existing_genres, migrations.RunPython.noop),
        migrations.AddField(model_name="order", name="address", field=models.ForeignKey(blank=True, db_column="address_id", null=True, on_delete=django.db.models.deletion.PROTECT, related_name="orders", to="shop.address")),
        migrations.AddField(model_name="stocklog", name="employee", field=models.ForeignKey(blank=True, db_column="employee_id", null=True, on_delete=django.db.models.deletion.PROTECT, related_name="stock_logs", to="shop.employee")),
        migrations.CreateModel(name="StockRequest", fields=[
            ("request_id", models.AutoField(primary_key=True, serialize=False)),
            ("requested_at", models.DateTimeField(auto_now_add=True)), ("notified", models.BooleanField(default=False)),
            ("customer", models.ForeignKey(db_column="customer_id", on_delete=django.db.models.deletion.CASCADE, related_name="stock_requests", to="shop.customer")),
            ("product", models.ForeignKey(db_column="product_id", on_delete=django.db.models.deletion.CASCADE, related_name="stock_requests", to="shop.product")),
        ], options={"db_table": "stock_requests"}),
        migrations.AddConstraint(model_name="stockrequest", constraint=models.UniqueConstraint(fields=("customer", "product"), name="unique_customer_product_stock_request")),
    ]
