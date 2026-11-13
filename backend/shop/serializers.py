from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Avg
from rest_framework import serializers

from .models import Address, Category, Order, OrderItem, Payment, Product, Review
from .services import available_quantity


class ProductSerializer(serializers.ModelSerializer):
    # Поле, которого нет в таблице: считаем, сколько можно купить с учётом броней
    available = serializers.SerializerMethodField()
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), required=False, allow_null=True
    )
    # Средняя оценка и число отзывов. Их считает база (annotate во views.py)
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "product_id", "product_name", "author", "genre", "category_id", "category_name",
            "price", "stock_quantity", "available", "last_updated",
            "avg_rating", "review_count",
        ]

    category_name = serializers.CharField(source="category.category_name", read_only=True, allow_null=True)

    def get_available(self, product):
        return max(available_quantity(product), 0)

    def get_avg_rating(self, product):
        # Если список пришёл без annotate (например, low-stock), считаем отдельным запросом
        if hasattr(product, "avg_rating"):
            value = product.avg_rating
        else:
            value = product.reviews.aggregate(avg=Avg("rating"))["avg"]
        return round(value, 1) if value is not None else None

    def get_review_count(self, product):
        if hasattr(product, "review_count"):
            return product.review_count
        return product.reviews.count()

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """Отзыв, который видят все: имя автора, звёзды, текст, дата."""

    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    # is_mine = true, если отзыв написал тот, кто сейчас смотрит страницу.
    # Email автора наружу не отдаём, только этот флажок.
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ["review_id", "customer_name", "rating", "comment", "created_at", "updated_at", "is_mine"]

    def get_is_mine(self, review):
        return review.customer.email == self.context.get("email")


class ReviewInputSerializer(serializers.Serializer):
    """Проверка того, что прислал Angular при добавлении отзыва."""

    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(max_length=1000, required=False, allow_blank=True, default="")


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["order_item_id", "product_id", "product_name", "quantity", "unit_price"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["payment_id", "transaction_id", "amount", "status", "paid_at"]


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    delivery_fee = serializers.IntegerField(read_only=True)
    address = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "order_id", "customer_id", "customer_name", "order_date", "status",
            "reserved_until", "total", "delivery_fee", "items", "payments", "delivery_method", "address",
        ]

    def get_address(self, order):
        if not order.address_id:
            return None
        return AddressSerializer(order.address).data


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "category_name", "description"]


class AddressSerializer(serializers.ModelSerializer):
    full_address = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = ["address_id", "city", "full_address", "within_city", "entrance", "apartment", "intercom_code", "floor", "is_default"]

    def get_full_address(self, address):
        return address.full_address or f"{address.street} {address.building}".strip()


class AddressCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    city = serializers.CharField(max_length=100)
    full_address = serializers.CharField(max_length=300)
    within_city = serializers.BooleanField(default=True)
    entrance = serializers.CharField(max_length=30, required=False, allow_blank=True)
    apartment = serializers.CharField(max_length=30, required=False, allow_blank=True)
    intercom_code = serializers.CharField(max_length=30, required=False, allow_blank=True)
    floor = serializers.CharField(max_length=30, required=False, allow_blank=True)
    is_default = serializers.BooleanField(default=True)


# --- Проверка входящих данных (то, что присылает Angular) ---

class CustomerInputSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=100)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)


class AddressInputSerializer(serializers.Serializer):
    city = serializers.CharField(max_length=100)
    full_address = serializers.CharField(max_length=300)
    within_city = serializers.BooleanField()
    entrance = serializers.CharField(max_length=30, required=False, allow_blank=True)
    apartment = serializers.CharField(max_length=30, required=False, allow_blank=True)
    intercom_code = serializers.CharField(max_length=30, required=False, allow_blank=True)
    floor = serializers.CharField(max_length=30, required=False, allow_blank=True)


class ItemInputSerializer(serializers.Serializer):
    product_id = serializers.CharField(max_length=6)
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderSerializer(serializers.Serializer):
    customer = CustomerInputSerializer()
    items = ItemInputSerializer(many=True, allow_empty=False)
    delivery_method = serializers.ChoiceField(choices=Order.DeliveryMethod.choices, default=Order.DeliveryMethod.DELIVERY)
    address = AddressInputSerializer(required=False)

    def validate(self, attrs):
        if not attrs.get("address"):
            raise serializers.ValidationError({"address": "Address is required for delivery."})
        return attrs


class PayOrderSerializer(serializers.Serializer):
    card_number = serializers.CharField(max_length=25)


class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError("This email is already registered.")
        return email

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages)
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["full_name"],
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
