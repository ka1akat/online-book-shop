from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from .models import Order, Product
from .serializers import (
    CreateOrderSerializer, OrderSerializer, PayOrderSerializer, ProductSerializer,
)
from .services import ShopError, create_order, expire_reservations, pay_order
from rest_framework.authentication import SessionAuthentication
from .permissions import IsWarehouseOrManager

class LowStockView(ListAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsWarehouseOrManager]
    serializer_class = ProductSerializer

class ProductListView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        expire_reservations()
        return Product.objects.order_by("product_id")


class LowStockView(ListAPIView):
    """SELECT ... FROM products WHERE stock_quantity < 10 ORDER BY stock_quantity;"""

    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(stock_quantity__lt=10).order_by("stock_quantity")


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        expire_reservations()
        return Order.objects.select_related("customer").prefetch_related(
            "items__product", "payments"
        )


@api_view(["POST"])
def create_order_view(request):
    data = CreateOrderSerializer(data=request.data)
    data.is_valid(raise_exception=True)  # если поля неправильные — ответ 400 с ошибками
    try:
        order = create_order(data.validated_data["customer"], data.validated_data["items"])
    except ShopError as e:
        return Response({"detail": e.message}, status=e.status_code)
    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def pay_order_view(request, pk):
    data = PayOrderSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    try:
        order = pay_order(pk, data.validated_data["card_number"])
    except ShopError as e:
        return Response({"detail": e.message}, status=e.status_code)
    return Response(OrderSerializer(order).data)
