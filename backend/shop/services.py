import uuid
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone

from .models import Customer, Order, OrderItem, Payment, Product, StockLog


class ShopError(Exception):
    """Ошибка бизнес-правила (например, книги нет в наличии). Показывается покупателю."""

    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def expire_reservations():
    """BR-01: заказы, которые не оплатили за 15 минут, становятся cancelled — бронь снимается."""
    Order.objects.filter(
        status=Order.Status.RESERVED, reserved_until__lte=timezone.now()
    ).update(status=Order.Status.CANCELLED)


def reserved_quantity(product):
    """Сколько штук этой книги сейчас забронировано неоплаченными заказами."""
    result = OrderItem.objects.filter(
        product=product,
        order__status=Order.Status.RESERVED,
        order__reserved_until__gt=timezone.now(),
    ).aggregate(total=Sum("quantity"))
    return result["total"] or 0


def available_quantity(product):
    """Сколько можно купить прямо сейчас = на складе минус забронировано."""
    return product.stock_quantity - reserved_quantity(product)


@transaction.atomic
def create_order(customer_data, items):
    """
    Шаг 1 главного действия: покупатель оформляет заказ.
    Книги бронируются на 15 минут, склад пока НЕ уменьшается.
    """
    if not items:
        raise ShopError("Корзина пуста.")

    expire_reservations()

    # Находим покупателя по email или создаём нового (телефон хранится один раз — в CUSTOMERS)
    customer, _ = Customer.objects.update_or_create(
        email=customer_data["email"].strip().lower(),
        defaults={
            "full_name": customer_data["full_name"].strip(),
            "phone": customer_data.get("phone", "").strip(),
        },
    )

    order = Order.objects.create(
        customer=customer,
        status=Order.Status.RESERVED,
        reserved_until=timezone.now() + timedelta(minutes=settings.RESERVATION_MINUTES),
    )

    for item in items:
        # select_for_update «блокирует» строку книги, пока идёт транзакция:
        # два покупателя не смогут одновременно забронировать последнюю книгу
        try:
            product = Product.objects.select_for_update().get(pk=item["product_id"])
        except Product.DoesNotExist:
            raise ShopError(f"Книга {item['product_id']} не найдена.", 404)

        quantity = int(item["quantity"])
        if quantity < 1:
            raise ShopError("Количество должно быть 1 или больше.")

        free = available_quantity(product)
        if quantity > free:
            # raise внутри @transaction.atomic = ROLLBACK: заказ и покупатель не сохранятся
            raise ShopError(
                f"«{product.product_name}»: в наличии только {max(free, 0)} шт.", 409
            )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=product.price,  # копируем цену: старый заказ хранит цену на момент покупки
        )

    return order


def fake_bank(card_number, amount):
    """
    Имитация банка. Настоящего банка нет, поэтому правило простое:
    карта, которая заканчивается на 0000, — «недостаточно средств».
    """
    digits = "".join(ch for ch in str(card_number) if ch.isdigit())
    if len(digits) != 16:
        raise ShopError("Номер карты должен состоять из 16 цифр.")
    transaction_id = "TX-" + uuid.uuid4().hex[:10].upper()
    approved = not digits.endswith("0000")
    return approved, transaction_id


def pay_order(order_id, card_number):
    """
    Шаг 2 главного действия: оплата.
    Транзакция из Task 9: уменьшить склад -> сохранить оплату -> статус paid -> запись в STOCK_LOG.
    Либо все шаги выполняются (COMMIT), либо ни один (ROLLBACK).
    """
    expire_reservations()

    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        raise ShopError("Заказ не найден.", 404)

    if order.status == Order.Status.PAID:
        raise ShopError("Этот заказ уже оплачен.", 409)
    if order.status == Order.Status.CANCELLED:
        raise ShopError("Бронь истекла (15 минут). Оформите заказ заново.", 409)

    amount = order.total
    approved, transaction_id = fake_bank(card_number, amount)

    if not approved:
        # Неудачная попытка тоже сохраняется: у заказа может быть много оплат (1:M)
        Payment.objects.create(
            order=order, transaction_id=transaction_id, amount=amount, status=Payment.Status.FAILED
        )
        raise ShopError("Банк отклонил оплату: недостаточно средств. Попробуйте другую карту.", 402)

    with transaction.atomic():  # BEGIN
        for item in order.items.select_related("product"):
            # UPDATE ... WHERE stock_quantity >= quantity — как в Task 9
            updated = Product.objects.filter(
                pk=item.product_id, stock_quantity__gte=item.quantity
            ).update(
                stock_quantity=F("stock_quantity") - item.quantity,
                last_updated=timezone.localdate(),
            )
            if updated == 0:
                # 0 строк изменилось -> книги нет -> ROLLBACK всей транзакции
                raise ShopError(f"«{item.product.product_name}» закончилась.", 409)

            StockLog.objects.create(
                product_id=item.product_id,
                changed_by="payment-system",
                change_amount=-item.quantity,
                reason="sale",
            )

        Payment.objects.create(
            order=order, transaction_id=transaction_id, amount=amount, status=Payment.Status.SUCCESS
        )
        order.status = Order.Status.PAID
        order.save(update_fields=["status"])
    # COMMIT — выход из блока with без ошибки

    return order
