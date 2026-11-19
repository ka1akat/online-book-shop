from decimal import Decimal, InvalidOperation

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core import signing
from django.db import transaction
from django.db.models import Avg, Count, F, Q, Sum
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Address, Category, Customer, Employee, Order, OrderItem, Payment, Product, Review, StockLog, StockRequest, StoreReview
from .permissions import IsManager, IsWarehouse, IsWarehouseOrManager
from .serializers import (
    AddressCreateSerializer, AddressSerializer, CategorySerializer, CreateOrderSerializer,
    LoginSerializer, OrderSerializer, PayOrderSerializer, ProductSerializer, RegisterSerializer,
    ReviewInputSerializer, ReviewSerializer, StoreReviewInputSerializer, StoreReviewSerializer,
)
from .services import ShopError, create_order, expire_reservations, pay_order


def products_with_rating():
    """Книги + средняя оценка и число отзывов, посчитанные самой базой.

    То же самое на SQL:
    SELECT p.*, AVG(r.rating) AS avg_rating, COUNT(r.review_id) AS review_count
    FROM products p LEFT JOIN reviews r ON r.product_id = p.product_id
    GROUP BY p.product_id;
    """
    return Product.objects.annotate(avg_rating=Avg("reviews__rating"), review_count=Count("reviews"))


def number_param(params, name):
    """Читает число из адреса (?min_price=3000). Пусто — фильтра нет, не число — ошибка 400."""
    raw = params.get(name, "").strip()
    if not raw:
        return None
    try:
        value = Decimal(raw)
    except InvalidOperation:
        raise ValidationError({name: "Must be a number."})
    if value < 0:
        raise ValidationError({name: "Cannot be negative."})
    return value


# --- Токен входа ---
# После входа Django выдаёт подписанную строку с id пользователя.
# Подделать её нельзя: подпись делается секретным ключом SECRET_KEY из settings.py.
# Angular присылает токен в заголовке Authorization, когда пишет отзыв.
TOKEN_SALT = "bookshop-auth"
TOKEN_MAX_AGE = 60 * 60 * 24 * 7  # токен действует 7 дней


def make_token(user):
    return signing.dumps({"user_id": user.id}, salt=TOKEN_SALT)


def user_from_token(request):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    try:
        data = signing.loads(header[len("Bearer "):], salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE)
    except signing.BadSignature:  # подделан или истёк срок
        return None
    return User.objects.filter(id=data.get("user_id"), is_active=True).first()


class LowStockView(ListAPIView):
    """SELECT ... FROM products WHERE stock_quantity < 10 ORDER BY stock_quantity;"""

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsWarehouseOrManager]
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(stock_quantity__lt=10).order_by("stock_quantity")


@api_view(["GET"])
@permission_classes([IsWarehouseOrManager])
def demand_report_view(request):
    """Return books ranked by the number of stock requests from customers."""
    report = (
        StockRequest.objects
        .values(
            "product_id",
            "product__product_name",
            "product__author",
            "product__category__category_name",
        )
        .annotate(request_count=Count("request_id"))
        .order_by("-request_count", "product__product_name", "product_id")
    )
    return Response([
        {
            "product_id": row["product_id"],
            "product_name": row["product__product_name"],
            "author": row["product__author"],
            "category_name": row["product__category__category_name"],
            "request_count": row["request_count"],
        }
        for row in report
    ])


@api_view(["GET"])
@permission_classes([IsManager])
def monthly_sales_report_view(request):
    """Summarize paid book sales by category for a month (YYYY-MM)."""
    from datetime import date
    from django.utils import timezone

    raw_month = request.query_params.get("month", "")
    try:
        month = date.fromisoformat(f"{raw_month}-01") if raw_month else timezone.localdate().replace(day=1)
    except ValueError:
        return Response({"month": "Use YYYY-MM format."}, status=status.HTTP_400_BAD_REQUEST)

    paid_order_ids = Payment.objects.filter(
        status=Payment.Status.SUCCESS,
        paid_at__year=month.year,
        paid_at__month=month.month,
    ).values("order_id")
    categories = (
        OrderItem.objects.filter(order_id__in=paid_order_ids)
        .values("product__category_id", "product__category__category_name")
        .annotate(
            units_sold=Sum("quantity"),
            revenue=Sum(F("quantity") * F("unit_price")),
        )
        .order_by("product__category__category_name")
    )
    return Response({
        "month": month.strftime("%Y-%m"),
        "categories": [
            {
                "category_id": row["product__category_id"],
                "category_name": row["product__category__category_name"],
                "units_sold": row["units_sold"],
                "revenue": row["revenue"],
            }
            for row in categories
        ],
    })


class ProductListView(ListCreateAPIView):
    serializer_class = ProductSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def get_permissions(self):
        if self.request.method == "POST":
            # создавать книги (то есть менять склад) может только склад и admin
            return [IsWarehouse()]
        return [AllowAny()]

    # Как можно отсортировать каталог: ?ordering=price / -price / -rating
    ORDERINGS = {
        "price": ["price", "product_id"],                    # сначала дешёвые
        "-price": ["-price", "product_id"],                  # сначала дорогие
        "-rating": [F("avg_rating").desc(nulls_last=True), "-review_count", "product_id"],
    }

    def get_queryset(self):
        expire_reservations()
        params = self.request.query_params
        queryset = products_with_rating().select_related("category")

        category_id = params.get("category_id")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        search = params.get("search")
        if search:
            queryset = queryset.filter(Q(product_name__icontains=search) | Q(author__icontains=search))

        # Фильтр по цене: ?min_price=3000&max_price=7000
        min_price = number_param(params, "min_price")
        max_price = number_param(params, "max_price")
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)

        # Фильтр по рейтингу: ?min_rating=4 — только книги со средней оценкой 4 и выше.
        # Книги без отзывов сюда не попадают: у них оценки ещё нет.
        min_rating = number_param(params, "min_rating")
        if min_rating is not None:
            queryset = queryset.filter(avg_rating__gte=min_rating)

        ordering = params.get("ordering", "")
        if ordering and ordering not in self.ORDERINGS:
            raise ValidationError({"ordering": f"Use one of: {', '.join(self.ORDERINGS)}."})
        return queryset.order_by(*self.ORDERINGS.get(ordering, ["product_id"]))

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


class ProductDetailView(RetrieveAPIView):
    """Одна книга со средней оценкой: GET /api/products/P-1001/"""

    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        expire_reservations()
        return products_with_rating().select_related("category")


@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def product_reviews_view(request, pk):
    """GET — все отзывы на книгу (видят все). POST — добавить или изменить свой отзыв (нужен вход)."""
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

    user = user_from_token(request)  # None, если посетитель не вошёл

    if request.method == "GET":
        reviews = product.reviews.select_related("customer").order_by("-created_at")
        context = {"email": user.email.lower() if user else None}
        return Response(ReviewSerializer(reviews, many=True, context=context).data)

    if user is None:
        return Response(
            {"detail": "Please log in to leave a review."}, status=status.HTTP_401_UNAUTHORIZED
        )
    data = ReviewInputSerializer(data=request.data)
    data.is_valid(raise_exception=True)

    # Отзыв привязан к таблице CUSTOMERS. Если покупатель ещё ничего не заказывал,
    # строки в CUSTOMERS у него нет — создаём её по email из аккаунта.
    customer, _ = Customer.objects.get_or_create(
        email=user.email.lower(), defaults={"full_name": user.first_name or user.email}
    )
    # Один покупатель — один отзыв на книгу: если отзыв уже есть, он обновляется
    review, created = Review.objects.update_or_create(
        customer=customer, product=product, defaults=data.validated_data
    )
    return Response(
        ReviewSerializer(review, context={"email": customer.email}).data,
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def store_reviews_view(request):
    user = user_from_token(request)
    if request.method == "GET":
        reviews = StoreReview.objects.select_related("customer").all()
        context = {"email": user.email.lower() if user else None}
        return Response(StoreReviewSerializer(reviews, many=True, context=context).data)

    if user is None:
        return Response({"detail": "Please log in to leave a shop review."}, status=status.HTTP_401_UNAUTHORIZED)
    data = StoreReviewInputSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    customer, _ = Customer.objects.get_or_create(
        email=user.email.lower(), defaults={"full_name": user.first_name or user.email}
    )
    review, created = StoreReview.objects.update_or_create(
        customer=customer,
        defaults=data.validated_data,
    )
    return Response(
        StoreReviewSerializer(review, context={"email": customer.email}).data,
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        expire_reservations()
        return Order.objects.select_related("customer", "address").prefetch_related(
            "items__product", "payments"
        )


@api_view(["POST"])
def create_order_view(request):
    data = CreateOrderSerializer(data=request.data)
    data.is_valid(raise_exception=True)  # если поля неправильные — ответ 400 с ошибками
    values = data.validated_data
    saved_address = None
    if values.get("saved_address_id"):
        user = user_from_token(request)
        if user is None or user.email.lower() != values["customer"]["email"].strip().lower():
            return Response({"detail": "Log in with this email to use a saved address."}, status=status.HTTP_401_UNAUTHORIZED)
        saved_address = Address.objects.filter(
            address_id=values["saved_address_id"],
            customer__email__iexact=values["customer"]["email"].strip(),
            is_saved=True,
        ).first()
        if saved_address is None:
            return Response({"detail": "Saved address not found for this customer."}, status=status.HTTP_404_NOT_FOUND)
    try:
        order = create_order(
            values["customer"], values["items"],
            values["delivery_method"], values.get("address"), saved_address=saved_address,
            save_address=values["save_address"],
        )
    except ShopError as e:
        return Response({"detail": e.message}, status=e.status_code)
    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class CategoryListView(ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    queryset = Category.objects.order_by("category_name")


@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def addresses_view(request):
    if request.method == "GET":
        email = request.query_params.get("email", "").strip().lower()
        if not email:
            return Response({"email": "Email query parameter is required."}, status=400)
        user = user_from_token(request)
        if user is None or user.email.lower() != email:
            return Response({"detail": "Log in with this email to view saved addresses."}, status=401)
        addresses = Address.objects.filter(customer__email=email, is_saved=True).order_by("-is_default", "address_id")
        return Response(AddressSerializer(addresses, many=True).data)

    data = AddressCreateSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    values = data.validated_data
    try:
        customer = Customer.objects.get(email=values.pop("email").lower())
    except Customer.DoesNotExist:
        return Response({"detail": "Customer not found. Create an order first."}, status=404)
    if values["is_default"]:
        Address.objects.filter(customer=customer, is_default=True).update(is_default=False)
    address = Address.objects.create(
        customer=customer,
        street=values["full_address"],
        building="",
        is_saved=True,
        **values,
    )
    return Response(AddressSerializer(address).data, status=201)


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
        {"id": user.id, "full_name": user.first_name, "email": user.email, "token": make_token(user)},
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
    return Response(
        {"id": user.id, "full_name": user.first_name, "email": user.email, "token": make_token(user)}
    )
