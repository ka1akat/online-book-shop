from django.contrib import admin
from django.db import transaction

from .models import Address, Category, Customer, Employee, Order, OrderItem, Payment, Product, StockLog, StockRequest
from .permissions import RoleAdminMixin


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
    list_display = ["address_id", "customer", "city", "street", "building", "is_default"]


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
    list_display = ["payment_id", "order", "transaction_id", "amount", "status", "paid_at"]


@admin.register(StockLog)
class StockLogAdmin(RoleAdminMixin, admin.ModelAdmin):
    view_roles = ["warehouse", "manager"]
    list_display = ["log_id", "product", "employee", "changed_by", "change_amount", "reason", "changed_at"]


@admin.register(StockRequest)
class StockRequestAdmin(RoleAdminMixin, admin.ModelAdmin):
    view_roles = ["warehouse", "support", "manager"]
    edit_roles = ["warehouse", "support", "manager"]
    list_display = ["request_id", "customer", "product", "requested_at", "notified"]


@admin.register(Employee)
class EmployeeAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["employee_id", "login", "full_name", "role", "is_active"]
    # эти поля Employee.save() заполняет сам из пользователя, руками их менять не нужно
    readonly_fields = ["login", "full_name", "password_hash", "is_active"]