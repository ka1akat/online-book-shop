from decimal import Decimal, InvalidOperation

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core import signing
from django.db import transaction
from django.db.models import Avg, Count, F, Q, Sum
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .models import Address, Category, Customer, Employee, Order, OrderItem, Payment, Product, Review, StockLog, StockRequest, StoreReview, SupportTicket, WishlistItem
from .permissions import IsManager, IsWarehouse, IsWarehouseOrManager
from .serializers import (
    AddressCreateSerializer, AddressSerializer, CategorySerializer, CreateOrderSerializer,
    LoginSerializer, OrderSerializer, PayOrderSerializer, ProductSerializer, RegisterSerializer,
    ReviewInputSerializer, ReviewSerializer, StoreReviewInputSerializer, StoreReviewSerializer, SupportRequestSerializer, SupportTicketSerializer,
    NotifyInputSerializer, StockRequestSerializer, WishlistInputSerializer, CustomerTicketSerializer,
    PreferencesInputSerializer,
)
from .moderation import check_support_message
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
    # Заказ открывается по секретному коду (UUID), а не по номеру 1, 2, 3...
    lookup_field = "public_code"
    lookup_url_kwarg = "code"

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
def pay_order_view(request, code):
    data = PayOrderSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    # Оплачивается заказ по секретному коду; по чужому номеру оплатить нельзя
    found = Order.objects.filter(public_code=code).first()
    if found is None:
        return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
    try:
        order = pay_order(found.pk, data.validated_data["card_number"])
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

class SupportThrottle(AnonRateThrottle):
    """Не больше 10 обращений в час с одного адреса: защита формы от спама."""

    scope = "support"
    rate = "10/hour"


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([SupportThrottle])
def support_view(request):
    """Покупатель пишет в поддержку по своему заказу.

    Кто пишет, определяется так: если есть токен входа, берём email аккаунта (email из тела
    запроса игнорируется). Если токена нет, нужен email, указанный при заказе.
    Заказ должен принадлежать этому email. Если заказа нет или он чужой, ответ один и тот же,
    чтобы нельзя было выяснить, существует ли чужой заказ.
    """
    data = SupportRequestSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    values = data.validated_data

    # Проверка текста ДО сохранения: мат, оскорбления, ссылки, набор букв.
    # Если проверка не пройдена, обращение в базу не попадает.
    problem = check_support_message(values["message"])
    if problem:
        return Response({"detail": problem}, status=status.HTTP_400_BAD_REQUEST)

    not_found = Response(
        {"detail": "We could not find this order. Please check the link or the e-mail."},
        status=status.HTTP_404_NOT_FOUND,
    )
    if "order_code" in values:
        # Секретный код заказа сам доказывает, что заказ ваш: email не нужен
        order = Order.objects.select_related("customer").filter(public_code=values["order_code"]).first()
    else:
        # Заказ указан номером: нужен email заказа или вход в аккаунт
        user = user_from_token(request)
        email = (user.email if user else values.get("email", "")).strip().lower()
        if not email:
            return Response(
                {"detail": "Please enter the e-mail that was used for the order."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order = Order.objects.select_related("customer").filter(
            pk=values["order_id"], customer__email=email
        ).first()
    if order is None:
        return not_found

    ticket = SupportTicket.objects.create(
        order=order, customer=order.customer, topic=values["topic"], message=values["message"],
    )
    return Response(SupportTicketSerializer(ticket).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def my_tickets_view(request):
    """Все обращения вошедшего покупателя со статусом и ответом поддержки.

    Покупатель определяется по токену, а не по email из запроса, поэтому чужие
    обращения и чужие ответы получить нельзя."""
    user = user_from_token(request)
    if user is None:
        return login_required_response("see your support requests")
    tickets = (
        SupportTicket.objects.filter(customer__email=user.email.lower())
        .select_related("order")
        .order_by("-created_at")
    )
    return Response(CustomerTicketSerializer(tickets, many=True).data)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def order_tickets_view(request, code):
    """Обращения по одному заказу. Секретный код заказа доказывает, что вы его владелец."""
    order = Order.objects.filter(public_code=code).first()
    if order is None:
        return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
    tickets = order.support_tickets.select_related("order").order_by("-created_at")
    return Response(CustomerTicketSerializer(tickets, many=True).data)


# ---------- Покупатель, который вошёл на сайт ----------

def customer_for_user(user):
    """Строка в CUSTOMERS для аккаунта сайта. Если покупатель ещё ничего не заказывал — создаём её."""
    customer, _ = Customer.objects.get_or_create(
        email=user.email.lower(), defaults={"full_name": user.first_name or user.email}
    )
    return customer


def login_required_response(action):
    return Response({"detail": f"Please log in to {action}."}, status=status.HTTP_401_UNAUTHORIZED)


# ---------- FR-07: лист ожидания «Notify me» и уведомления ----------

@api_view(["POST", "DELETE"])
@authentication_classes([])
@permission_classes([AllowAny])
def product_notify_view(request, pk):
    """
    POST — покупатель нажал «Notify me» на книге, которой нет на складе.
           Тот же покупатель + та же книга второй раз -> всё равно одна строка (UNIQUE).
    DELETE — покупатель больше не ждёт книгу (нужен вход).
    """
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)

    user = user_from_token(request)

    if request.method == "DELETE":
        if user is None:
            return login_required_response("manage your waiting list")
        StockRequest.objects.filter(customer__email=user.email.lower(), product=product).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Критерий 1: ждать можно только книгу, которой нет на складе
    if product.stock_quantity > 0:
        return Response(
            {"detail": "This book is in stock, you can order it now."}, status=status.HTTP_400_BAD_REQUEST
        )

    data = NotifyInputSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    if user:
        customer = customer_for_user(user)  # email из аккаунта, email из тела запроса не важен
    else:
        email = data.validated_data.get("email", "").strip().lower()
        if not email:
            return Response({"email": "Please enter your e-mail."}, status=status.HTTP_400_BAD_REQUEST)
        customer, _ = Customer.objects.get_or_create(email=email, defaults={"full_name": email})

    # Критерий 2: get_or_create — если строка уже есть, новую не создаём
    stock_request, created = StockRequest.objects.get_or_create(customer=customer, product=product)
    if not created and stock_request.notified:
        # Книгу уже привозили, а она снова закончилась: человек снова ждёт
        stock_request.notified = False
        stock_request.notified_at = None
        stock_request.is_read = False
        stock_request.save(update_fields=["notified", "notified_at", "is_read"])
    return Response(
        StockRequestSerializer(stock_request).data,
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def notifications_view(request):
    """Мой лист ожидания: сначала книги, которые уже вернулись (это и есть уведомления), потом те, что ещё ждём."""
    user = user_from_token(request)
    if user is None:
        return login_required_response("see your notifications")
    requests = (
        StockRequest.objects.filter(customer__email=user.email.lower())
        .select_related("product")
        .order_by("-notified", F("notified_at").desc(nulls_last=True), "-requested_at")
    )
    return Response(StockRequestSerializer(requests, many=True).data)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def notifications_read_view(request):
    """Покупатель открыл страницу уведомлений — отмечаем их прочитанными, счётчик в меню обнуляется."""
    user = user_from_token(request)
    if user is None:
        return login_required_response("see your notifications")
    updated = StockRequest.objects.filter(
        customer__email=user.email.lower(), notified=True, is_read=False
    ).update(is_read=True)
    return Response({"marked_read": updated})


# ---------- Мои заказы ----------

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def my_orders_view(request):
    """Все заказы покупателя, который вошёл. Покупатель определяется по токену, а не по email из запроса."""
    user = user_from_token(request)
    if user is None:
        return login_required_response("see your orders")
    expire_reservations()  # просроченные брони сразу показываются как cancelled
    orders = (
        Order.objects.filter(customer__email=user.email.lower())
        .select_related("customer", "address")
        .prefetch_related("items__product", "payments")
        .order_by("-order_date")
    )
    return Response(OrderSerializer(orders, many=True).data)


# ---------- Wishlist (избранное) ----------

@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def wishlist_view(request):
    """GET — мои отложенные книги. POST {product_id} — добавить книгу (второй раз не дублируется)."""
    user = user_from_token(request)
    if user is None:
        return login_required_response("use your wishlist")
    customer = customer_for_user(user)

    if request.method == "GET":
        ids = list(customer.wishlist_items.order_by("-added_at").values_list("product_id", flat=True))
        products = {p.product_id: p for p in products_with_rating().select_related("category").filter(pk__in=ids)}
        # порядок как в избранном: последние добавленные сверху
        return Response(ProductSerializer([products[i] for i in ids if i in products], many=True).data)

    data = WishlistInputSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    product = Product.objects.filter(pk=data.validated_data["product_id"]).first()
    if product is None:
        return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
    _, created = WishlistItem.objects.get_or_create(customer=customer, product=product)
    return Response(
        {"product_id": product.product_id, "in_wishlist": True},
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@authentication_classes([])
@permission_classes([AllowAny])
def wishlist_item_view(request, pk):
    """Убрать книгу из моего избранного."""
    user = user_from_token(request)
    if user is None:
        return login_required_response("use your wishlist")
    WishlistItem.objects.filter(customer__email=user.email.lower(), product_id=pk).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ---------- Top rating: лучшие книги по оценкам покупателей ----------

def limit_param(params, default, maximum):
    """?limit=5 -> 5. Пусто -> default. Больше maximum -> maximum."""
    value = number_param(params, "limit")
    if value is None:
        return default
    return max(1, min(int(value), maximum))


def ranked_by_rating(queryset):
    """Сначала самая высокая средняя оценка; при равной — у кого больше отзывов."""
    return queryset.order_by(F("avg_rating").desc(nulls_last=True), "-review_count", "product_id")


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def top_rated_view(request):
    """
    GET /api/products/top-rated/?limit=10&category_id=2
    Рейтинг книг: только книги, у которых есть хотя бы один отзыв (без оценок места в рейтинге нет).
    То же на SQL: ... GROUP BY p.product_id HAVING COUNT(r.review_id) >= 1
                  ORDER BY AVG(r.rating) DESC, COUNT(r.review_id) DESC LIMIT 10
    """
    params = request.query_params
    books = products_with_rating().select_related("category").filter(review_count__gte=1)
    category_id = params.get("category_id")
    if category_id:
        books = books.filter(category_id=category_id)
    books = ranked_by_rating(books)[: limit_param(params, 10, 50)]
    return Response(ProductSerializer(books, many=True).data)


# ---------- Preferable list: похожие книги и подборка «For you» ----------

@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def similar_products_view(request, pk):
    """GET /api/products/P-1001/similar/ — «You may also like»: книги той же категории, лучшие сверху."""
    product = Product.objects.filter(pk=pk).first()
    if product is None:
        return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
    limit = limit_param(request.query_params, 4, 12)
    books = list(ranked_by_rating(
        products_with_rating().select_related("category").filter(category_id=product.category_id).exclude(pk=pk)
    )[:limit])
    if len(books) < limit:
        # в категории мало книг — добавляем лучшие книги из других категорий
        taken = [b.pk for b in books] + [pk]
        books += list(ranked_by_rating(
            products_with_rating().select_related("category").exclude(pk__in=taken)
        )[: limit - len(books)])
    return Response(ProductSerializer(books, many=True).data)


@api_view(["GET", "PUT"])
@authentication_classes([])
@permission_classes([AllowAny])
def preferences_view(request):
    """GET — мои любимые категории. PUT {category_ids: [1, 3]} — сохранить выбор (заменяет старый)."""
    user = user_from_token(request)
    if user is None:
        return login_required_response("choose your favourite categories")
    customer = customer_for_user(user)
    if request.method == "PUT":
        data = PreferencesInputSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        ids = set(data.validated_data["category_ids"])
        categories = list(Category.objects.filter(pk__in=ids))
        if len(categories) != len(ids):
            return Response({"category_ids": "Unknown category."}, status=status.HTTP_400_BAD_REQUEST)
        customer.favorite_categories.set(categories)
    return Response({"category_ids": sorted(customer.favorite_categories.values_list("pk", flat=True))})


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def recommendations_view(request):
    """
    GET /api/recommendations/ — подборка «For you» для покупателя, который вошёл.
    1) Если он выбрал любимые категории — книги из них.
    2) Если нет — категории из его действий: избранное, заказы, отзывы с оценкой 4–5.
    3) Если и действий нет — просто лучшие книги (Top rated).
    Книги, которые уже в избранном или уже куплены, не предлагаем.
    """
    user = user_from_token(request)
    if user is None:
        return login_required_response("see books picked for you")
    customer = customer_for_user(user)
    limit = limit_param(request.query_params, 8, 24)

    category_ids = set(customer.favorite_categories.values_list("pk", flat=True))
    based_on = "favorites"
    if not category_ids:
        based_on = "activity"
        category_ids |= set(customer.wishlist_items.values_list("product__category_id", flat=True))
        category_ids |= set(
            OrderItem.objects.filter(order__customer=customer).exclude(order__status="cancelled")
            .values_list("product__category_id", flat=True)
        )
        category_ids |= set(customer.reviews.filter(rating__gte=4).values_list("product__category_id", flat=True))
        category_ids.discard(None)

    seen = set(customer.wishlist_items.values_list("product_id", flat=True))
    seen |= set(OrderItem.objects.filter(order__customer=customer, order__status="paid").values_list("product_id", flat=True))

    books = products_with_rating().select_related("category").exclude(pk__in=seen)
    if category_ids:
        books = books.filter(category_id__in=category_ids)
    else:
        based_on = "top_rated"
    books = list(ranked_by_rating(books)[:limit])
    return Response({
        "based_on": based_on,
        "categories": list(Category.objects.filter(pk__in=category_ids).order_by("category_name")
                           .values_list("category_name", flat=True)),
        "books": ProductSerializer(books, many=True).data,
    })

