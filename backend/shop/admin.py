from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from .models import Address, Category, Customer, Employee, Order, OrderItem, Payment, Product, Review, StockLog, StockRequest, StoreReview, SupportTicket, WishlistItem
from .permissions import RoleAdminMixin, get_role
from .services import ShopError, notify_waiting_customers, refund_payment


@admin.register(Product)
class ProductAdmin(RoleAdminMixin, admin.ModelAdmin):
    edit_roles = ["warehouse"]
    view_roles = ["finance", "manager"]
    list_display = ["product_id", "product_name", "author", "category", "genre", "price", "stock_quantity"]
    list_editable = ["stock_quantity"]

    def save_model(self, request, obj, form, change):
        # Каждое изменение склада сотрудником пишется в STOCK_LOG с его личным логином.
        # Склад и лог сохраняются в одной транзакции: либо оба, либо ни одного.
        old_stock = None
        if change and "stock_quantity" in form.changed_data:
            old_stock = Product.objects.get(pk=obj.pk).stock_quantity
        with transaction.atomic():
            super().save_model(request, obj, form, change)
            if old_stock is not None and obj.stock_quantity != old_stock:
                diff = obj.stock_quantity - old_stock
                StockLog.objects.create(
                    product=obj,
                    changed_by=request.user.username,
                    employee=Employee.objects.filter(user=request.user).first(),
                    change_amount=diff,
                    reason="delivery" if diff > 0 else "correction",
                )
        # Книга вернулась на склад — уведомляем тех, кто её ждал (FR-07, критерий 4)
        if obj.stock_quantity > 0:
            notify_waiting_customers(obj.pk)


@admin.register(Customer)
class CustomerAdmin(RoleAdminMixin, admin.ModelAdmin):
    view_roles = ["finance", "manager", "support"]
    list_display = ["customer_id", "full_name", "email", "phone", "registered_at"]


@admin.register(Category)
class CategoryAdmin(RoleAdminMixin, admin.ModelAdmin):
    view_roles = ["warehouse", "finance", "manager", "support"]
    edit_roles = ["warehouse", "manager"]
    list_display = ["category_id", "category_name"]


@admin.register(Address)
class AddressAdmin(RoleAdminMixin, admin.ModelAdmin):
    view_roles = ["support", "finance", "manager"]
    edit_roles = ["support", "manager"]
    list_display = [
        "address_id", "customer", "city", "full_address", "within_city",
        "entrance", "apartment", "intercom_code", "floor", "is_default",
    ]
    list_filter = ["city", "within_city", "is_default"]
    search_fields = ["customer__full_name", "customer__email", "city", "full_address"]
    fields = [
        "customer", "city", "full_address", "within_city", "entrance",
        "apartment", "intercom_code", "floor", "is_default",
    ]


class OrderItemInline(RoleAdminMixin, admin.TabularInline):
    model = OrderItem
    extra = 0
    # склад здесь больше не видит заказы, поэтому его нет в списке
    view_roles = ["finance", "manager", "support"]


class PaymentInline(RoleAdminMixin, admin.TabularInline):
    model = Payment
    extra = 0
    view_roles = ["finance", "manager"]


@admin.register(Order)
class OrderAdmin(RoleAdminMixin, admin.ModelAdmin):
    edit_roles = ["finance", "support"]
    # склад убран: в заказах видны имя, email и адрес покупателя (чувствительные данные)
    view_roles = ["manager"]
    list_display = ["order_id", "customer", "address", "status", "order_date", "reserved_until"]
    list_filter = ["status"]
    inlines = [OrderItemInline, PaymentInline]


@admin.register(Payment)
class PaymentAdmin(RoleAdminMixin, admin.ModelAdmin):
    view_roles = ["finance", "manager"]
    list_display = ["payment_id", "order", "transaction_id", "amount", "status",
                    "refund_reason", "refunded_at", "paid_at"]
    list_filter = ["status"]
    actions = ["refund_changed_mind", "refund_defective", "refund_other"]

    def has_refund_permission(self, request):
        # возврат могут делать только finance и admin
        return get_role(request.user) in ["finance", "admin"]

    def _refund(self, request, queryset, reason):
        employee = Employee.objects.filter(user=request.user).first()
        done = 0
        for payment in queryset:
            try:
                refund_payment(payment.pk, employee=employee,
                               changed_by=request.user.username, reason=reason)
                done += 1
            except ShopError as error:
                self.message_user(request, f"Payment {payment.pk}: {error.message}",
                                  level=messages.ERROR)
        if done:
            self.message_user(request, f"Refunded payments: {done}", level=messages.SUCCESS)

    @admin.action(description="Refund selected: customer changed mind", permissions=["refund"])
    def refund_changed_mind(self, request, queryset):
        self._refund(request, queryset, "changed_mind")

    @admin.action(description="Refund selected: defective item", permissions=["refund"])
    def refund_defective(self, request, queryset):
        self._refund(request, queryset, "defective")

    @admin.action(description="Refund selected: other reason", permissions=["refund"])
    def refund_other(self, request, queryset):
        self._refund(request, queryset, "other")
    
    def has_delete_permission(self, request, obj=None):
        # платежи не удаляются никем (даже admin): история денег должна сохраняться, для отмены есть возврат
        return False


@admin.register(StockLog)
class StockLogAdmin(RoleAdminMixin, admin.ModelAdmin):
    view_roles = ["warehouse", "manager"]
    list_display = ["log_id", "product", "employee", "changed_by", "change_amount", "reason", "changed_at"]


@admin.register(StockRequest)
class StockRequestAdmin(RoleAdminMixin, admin.ModelAdmin):
    view_roles = ["warehouse", "support", "manager"]
    edit_roles = ["warehouse", "support", "manager"]
    list_display = ["request_id", "customer", "product", "requested_at", "notified", "notified_at"]
    list_filter = ["notified"]


@admin.register(WishlistItem)
class WishlistItemAdmin(RoleAdminMixin, admin.ModelAdmin):
    # Избранное — данные покупателя: сотрудники только смотрят (менеджер видит, что люди хотят купить)
    view_roles = ["manager", "support"]
    list_display = ["wishlist_item_id", "customer", "product", "added_at"]
    search_fields = ["customer__email", "product__product_name"]


@admin.register(Review)
class ReviewAdmin(RoleAdminMixin, admin.ModelAdmin):
    # Поддержка и менеджер видят отзывы и могут удалить грубый или спам
    view_roles = ["support", "manager"]
    edit_roles = ["support", "manager"]
    list_display = ["review_id", "product", "customer", "rating", "created_at"]
    list_filter = ["rating"]
    search_fields = ["product__product_name", "customer__email", "comment"]


@admin.register(StoreReview)
class StoreReviewAdmin(RoleAdminMixin, admin.ModelAdmin):
    view_roles = ["support", "manager"]
    edit_roles = ["support", "manager"]
    list_display = ["review_id", "customer", "rating", "created_at"]
    list_filter = ["rating"]
    search_fields = ["customer__full_name", "customer__email", "comment"]

@admin.register(SupportTicket)
class SupportTicketAdmin(RoleAdminMixin, admin.ModelAdmin):
    # support обрабатывает обращения; manager и finance только читают; склад не видит
    edit_roles = ["support"]
    view_roles = ["finance", "manager"]
    list_display = ["ticket_id", "order", "customer", "topic", "status", "created_at", "handled_by"]
    list_filter = ["status", "topic"]
    # Текст покупателя менять нельзя: сотрудник меняет только статус
    readonly_fields = ["order", "customer", "topic", "message", "created_at", "handled_by", "closed_at"]
    actions = ["take_in_work", "close_selected"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if get_role(request.user) == "finance":
            # финансист видит только обращения по возврату
            queryset = queryset.filter(topic=SupportTicket.Topic.REFUND)
        return queryset

    def has_add_permission(self, request, obj=None):
        return False  # обращения создаёт только покупатель через сайт

    def has_delete_permission(self, request, obj=None):
        return False  # история обращений не удаляется

    def has_handle_permission(self, request):
        return get_role(request.user) in ["support", "admin"]

    def save_model(self, request, obj, form, change):
        if "status" in form.changed_data:
            if obj.handled_by is None:
                obj.handled_by = Employee.objects.filter(user=request.user).first()
            obj.closed_at = timezone.now() if obj.status == SupportTicket.Status.CLOSED else None
        super().save_model(request, obj, form, change)

    @admin.action(description="Take selected tickets into work", permissions=["handle"])
    def take_in_work(self, request, queryset):
        employee = Employee.objects.filter(user=request.user).first()
        done = queryset.filter(status=SupportTicket.Status.OPEN).update(
            status=SupportTicket.Status.IN_PROGRESS, handled_by=employee
        )
        self.message_user(request, f"Tickets taken into work: {done}", level=messages.SUCCESS)

    @admin.action(description="Close selected tickets", permissions=["handle"])
    def close_selected(self, request, queryset):
        employee = Employee.objects.filter(user=request.user).first()
        done = 0
        for ticket in queryset.exclude(status=SupportTicket.Status.CLOSED):
            ticket.status = SupportTicket.Status.CLOSED
            ticket.closed_at = timezone.now()
            if ticket.handled_by is None:
                ticket.handled_by = employee
            ticket.save()
            done += 1
        self.message_user(request, f"Tickets closed: {done}", level=messages.SUCCESS)

@admin.register(Employee)
class EmployeeAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["employee_id", "login", "full_name", "role", "is_active"]
    # эти поля Employee.save() заполняет сам из пользователя, руками их менять не нужно
    readonly_fields = ["login", "full_name", "password_hash", "is_active"]


# --- Страница пользователя: роль выбирается здесь же ---

class EmployeeInline(admin.StackedInline):
    model = Employee
    fields = ["role"]
    extra = 1
    max_num = 1
    can_delete = False


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Обычная страница пользователя + блок Employee с выбором роли.
    # После сохранения разрешения роли появляются в окне «User permissions».
    inlines = [EmployeeInline]
