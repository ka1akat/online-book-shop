from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Employee, Order, Product, StockLog
from .permissions import IsWarehouse, IsWarehouseOrManager
from .serializers import (
    CreateOrderSerializer, LoginSerializer, OrderSerializer, PayOrderSerializer,
    ProductSerializer, RegisterSerializer,
)
from .services import ShopError, create_order, expire_reservations, pay_order


class LowStockView(ListAPIView):
    """SELECT ... FROM products WHERE stock_quantity < 10 ORDER BY stock_quantity;"""

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsWarehouseOrManager]
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(stock_quantity__lt=10).order_by("stock_quantity")


class ProductListView(ListCreateAPIView):
    serializer_class = ProductSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def get_permissions(self):
        if self.request.method == "POST":
            # создавать книги (то есть менять склад) может только склад и admin
            return [IsWarehouse()]
        return [AllowAny()]

    def get_queryset(self):
        expire_reservations()
        return Product.objects.order_by("product_id")

    def perform_create(self, serializer):
        # Новая книга с остатком = поставка: пишем её в STOCK_LOG с логином сотрудника
        with transaction.atomic():
            product = serializer.save()
            if product.stock_quantity > 0:
                StockLog.objects.create(
                    product=product,
                    changed_by=self.request.user.username,
                    employee=Employee.objects.filter(user=self.request.user).first(),
                    change_amount=product.stock_quantity,
                    reason="delivery",
                )


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


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def register_view(request):
    data = RegisterSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    user = data.save()
    return Response(
        {"id": user.id, "full_name": user.first_name, "email": user.email},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def login_view(request):
    data = LoginSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    user = authenticate(
        request,
        username=data.validated_data["email"].lower(),
        password=data.validated_data["password"],
    )
    if user is None:
        return Response(
            {"detail": "Incorrect email or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    return Response({"id": user.id, "full_name": user.first_name, "email": user.email})