from django.db import models
from django.conf import settings

class Employee(models.Model):
    ROLES = [
        ("warehouse", "Warehouse"),
        ("finance", "Finance"),
        ("support", "Support"),
        ("manager", "Manager"),
        ("admin", "Admin"),
    ]
    employee_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    login = models.CharField(max_length=150, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=150, blank=True)
    password_hash = models.CharField(max_length=128, blank=True)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=20, choices=ROLES)

    def save(self, *args, **kwargs):
        if self.user_id:
            self.login = self.user.get_username()
            self.full_name = self.user.get_full_name() or self.user.get_username()
            self.password_hash = self.user.password
            self.is_active = self.user.is_active
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Customer(models.Model):
    """CUSTOMERS — кто покупает."""

    customer_id = models.AutoField(primary_key=True)  # PK, номер ставится автоматически
    full_name = models.CharField(max_length=100)  # обязательное поле
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=100, unique=True)  # UNIQUE: два одинаковых email нельзя
    registered_at = models.DateField(auto_now_add=True)  # дата ставится сама

    class Meta:
        db_table = "customers"

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class Address(models.Model):
    address_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="addresses")
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=150)
    building = models.CharField(max_length=30)
    apartment = models.CharField(max_length=30, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "addresses"

    def __str__(self):
        return f"{self.city}, {self.street} {self.building}"


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "categories"

    def __str__(self):
        return self.category_name


class Product(models.Model):
    """PRODUCTS — какие книги продаём и сколько их на складе."""

    product_id = models.CharField(max_length=6, primary_key=True)  # PK, формат P-1001
    product_name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    genre = models.CharField(max_length=30)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True, db_column="category_id", related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)  # цена в KZT
    stock_quantity = models.IntegerField()  # сколько штук на складе
    last_updated = models.DateField(auto_now=True)  # обновляется при каждом сохранении

    class Meta:
        db_table = "products"
        constraints = [
            # CHECK: на складе не может быть меньше 0 книг
            models.CheckConstraint(
                condition=models.Q(stock_quantity__gte=0), name="stock_not_negative"
            ),
            # CHECK: цена больше 0
            models.CheckConstraint(condition=models.Q(price__gt=0), name="price_positive"),
        ]

    def __str__(self):
        return f"{self.product_id} {self.product_name}"


class Order(models.Model):
    """ORDERS — одна покупка одного покупателя."""

    class Status(models.TextChoices):
        RESERVED = "reserved"  # заказ создан, книги забронированы на 15 минут
        PAID = "paid"  # оплачен, склад уменьшен
        CANCELLED = "cancelled"  # бронь истекла или заказ отменён

    order_id = models.AutoField(primary_key=True)
    # FK -> CUSTOMERS. PROTECT = ON DELETE RESTRICT: нельзя удалить покупателя, у которого есть заказы
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, db_column="customer_id", related_name="orders"
    )
    address = models.ForeignKey("Address", on_delete=models.PROTECT, null=True, blank=True, db_column="address_id", related_name="orders")
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.RESERVED)
    reserved_until = models.DateTimeField()  # время заказа + 15 минут (BR-01)

    class Meta:
        db_table = "orders"

    def __str__(self):
        return f"Order {self.order_id} ({self.status})"

    @property
    def total(self):
        return sum(item.quantity * item.unit_price for item in self.items.all())


class OrderItem(models.Model):
    """ORDER_ITEMS — какие книги лежат в заказе (bridge table для связи M:N)."""

    order_item_id = models.AutoField(primary_key=True)
    # FK -> ORDERS. CASCADE: если удалить сам заказ, его строки удаляются вместе с ним
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, db_column="order_id", related_name="items"
    )
    # FK -> PRODUCTS. PROTECT: нельзя удалить книгу, которая есть в заказах
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, db_column="product_id", related_name="order_items"
    )
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # цена в момент покупки

    class Meta:
        db_table = "order_items"
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gte=1), name="quantity_at_least_1"),
        ]


class Payment(models.Model):
    """PAYMENTS — ответ банка. У одного заказа может быть несколько попыток (1:M)."""

    class Status(models.TextChoices):
        SUCCESS = "success"
        FAILED = "failed"
        REFUNDED = "refunded"

    payment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, db_column="order_id", related_name="payments"
    )
    transaction_id = models.CharField(max_length=40, unique=True)  # UNIQUE: нет двойной обработки
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices)
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"


class StockLog(models.Model):
    """STOCK_LOG — история каждого изменения склада (кто, на сколько, когда, почему)."""

    log_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, db_column="product_id", related_name="stock_logs"
    )
    changed_by = models.CharField(max_length=50)  # логин сотрудника или 'payment-system'
    change_amount = models.IntegerField()  # например -1 после продажи, +20 при поставке
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True, blank=True, db_column="employee_id", related_name="stock_logs")
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=20)  # sale, delivery, correction

    class Meta:
        db_table = "stock_log"


class StockRequest(models.Model):
    request_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column="customer_id", related_name="stock_requests")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_column="product_id", related_name="stock_requests")
    requested_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    class Meta:
        db_table = "stock_requests"
        constraints = [models.UniqueConstraint(fields=["customer", "product"], name="unique_customer_product_stock_request")]
