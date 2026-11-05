from django.contrib import admin

from .models import Customer, Employee, Order, OrderItem, Payment, Product, StockLog
from .permissions import RoleAdminMixin


@admin.register(Product)
class ProductAdmin(RoleAdminMixin, admin.ModelAdmin):
    edit_roles = ["warehouse"]
    view_roles = ["finance", "manager"]
    list_display = ["product_id", "product_name", "author", "genre", "price", "stock_quantity"]
    list_editable = ["stock_quantity"]


@admin.register(Customer)
class CustomerAdmin(RoleAdminMixin, admin.ModelAdmin):
    view_roles = ["finance", "manager", "support"]
    list_display = ["customer_id", "full_name", "email", "phone", "registered_at"]


class OrderItemInline(RoleAdminMixin, admin.TabularInline):
    model = OrderItem
    extra = 0
    view_roles = ["finance", "warehouse", "manager", "support"]


class PaymentInline(RoleAdminMixin, admin.TabularInline):
    model = Payment
    extra = 0
    view_roles = ["finance", "manager"]


@admin.register(Order)
class OrderAdmin(RoleAdminMixin, admin.ModelAdmin):
    edit_roles = ["finance", "support"]
    view_roles = ["warehouse", "manager"]
    list_display = ["order_id", "customer", "status", "order_date", "reserved_until"]
    list_filter = ["status"]
    inlines = [OrderItemInline, PaymentInline]


@admin.register(Payment)
class PaymentAdmin(RoleAdminMixin, admin.ModelAdmin):
    view_roles = ["finance", "manager"]
    list_display = ["payment_id", "order", "transaction_id", "amount", "status", "paid_at"]


@admin.register(StockLog)
class StockLogAdmin(RoleAdminMixin, admin.ModelAdmin):
    view_roles = ["warehouse", "manager"]
    list_display = ["log_id", "product", "changed_by", "change_amount", "reason", "changed_at"]


@admin.register(Employee)
class EmployeeAdmin(RoleAdminMixin, admin.ModelAdmin):
    list_display = ["user", "role"]