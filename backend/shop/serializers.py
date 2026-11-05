from rest_framework import serializers

from .models import Order, OrderItem, Payment, Product
from .services import available_quantity


class ProductSerializer(serializers.ModelSerializer):
    # Поле, которого нет в таблице: считаем, сколько можно купить с учётом броней
    available = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "product_id", "product_name", "author", "genre",
            "price", "stock_quantity", "available", "last_updated",
        ]

    def get_available(self, product):
        return max(available_quantity(product), 0)


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

    class Meta:
        model = Order
        fields = [
            "order_id", "customer_id", "customer_name", "order_date", "status",
            "reserved_until", "total", "items", "payments",
        ]


# --- Проверка входящих данных (то, что присылает Angular) ---

class CustomerInputSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=100)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)


class ItemInputSerializer(serializers.Serializer):
    product_id = serializers.CharField(max_length=6)
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderSerializer(serializers.Serializer):
    customer = CustomerInputSerializer()
    items = ItemInputSerializer(many=True, allow_empty=False)


class PayOrderSerializer(serializers.Serializer):
    card_number = serializers.CharField(max_length=25)
