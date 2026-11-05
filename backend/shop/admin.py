
from django.contrib import admin

from .models import Customer, Order, OrderItem, Payment, Product, StockLog


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["product_id", "product_name", "author", "genre", "price", "stock_quantity"]
    list_editable = ["stock_quantity"]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["customer_id", "full_name", "email", "phone", "registered_at"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_id", "customer", "status", "order_date", "reserved_until"]
    list_filter = ["status"]
    inlines = [OrderItemInline, PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["payment_id", "order", "transaction_id", "amount", "status", "paid_at"]


@admin.register(StockLog)
class StockLogAdmin(admin.ModelAdmin):
    list_display = ["log_id", "product", "changed_by", "change_amount", "reason", "changed_at"]
