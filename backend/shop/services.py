import uuid
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone

from .models import Address, Customer, Order, OrderItem, Payment, Product, StockLog, StockRequest


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
def create_order(customer_data, items, delivery_method=Order.DeliveryMethod.DELIVERY, address_data=None, saved_address=None, save_address=False):
    """
    Шаг 1 главного действия: покупатель оформляет заказ.
    Книги бронируются на 15 минут, склад пока НЕ уменьшается.
    """
    if not items:
        raise ShopError("Your cart is empty.")

    expire_reservations()

    # Находим покупателя по email или создаём нового (телефон хранится один раз — в CUSTOMERS)
    customer, _ = Customer.objects.update_or_create(
        email=customer_data["email"].strip().lower(),
        defaults={
            "full_name": customer_data["full_name"].strip(),
            "phone": customer_data.get("phone", "").strip(),
        },
    )

    if not address_data and saved_address is None:
        raise ShopError("Please enter a delivery address.")
    if saved_address is not None:
        if saved_address.customer_id != customer.customer_id:
            raise ShopError("Saved address does not belong to this customer.", 404)
        address = saved_address
    else:
        if save_address:
            Address.objects.filter(customer=customer, is_default=True).update(is_default=False)
        address = Address.objects.create(
            customer=customer,
            is_saved=save_address,
            is_default=save_address,
            street=address_data["full_address"],
            building="",
            **address_data,
        )

    order = Order.objects.create(
        customer=customer,
        address=address,
        delivery_method=delivery_method,
        status=Order.Status.RESERVED,
        reserved_until=timezone.now() + timedelta(minutes=settings.RESERVATION_MINUTES),
    )

    for item in items:
        # select_for_update «блокирует» строку книги, пока идёт транзакция:
        # два покупателя не смогут одновременно забронировать последнюю книгу
        try:
            product = Product.objects.select_for_update().get(pk=item["product_id"])
        except Product.DoesNotExist:
            raise ShopError(f"Book {item['product_id']} not found.", 404)

        quantity = int(item["quantity"])
        if quantity < 1:
            raise ShopError("Quantity must be 1 or more.")

        free = available_quantity(product)
        if quantity > free:
            # raise внутри @transaction.atomic = ROLLBACK: заказ и покупатель не сохранятся
            raise ShopError(
                f"\"{product.product_name}\": only {max(free, 0)} in stock.", 409
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
        raise ShopError("The card number must have 16 digits.")
    transaction_id = "TX-" + uuid.uuid4().hex[:10].upper()
    approved = not digits.endswith("0000")
    return approved, transaction_id


def pay_order(order_id, card_number):
    """
    Шаг 2 главного действия: оплата.
    Транзакция из Task 9: уменьшить склад -> сохранить оплату -> статус paid -> запись в STOCK_LOG.
    Либо все шаги выполняются (COMMIT), либо ни один (ROLLBACK).
    Защита от двойного клика: строка заказа блокируется, второй запрос ждёт и видит статус paid.
    """
    expire_reservations()

    declined = False
    with transaction.atomic():  # BEGIN
        # Блокируем заказ: пока идёт эта оплата, другой запрос на этот же заказ ждёт здесь
        try:
            order = Order.objects.select_for_update().get(pk=order_id)
        except Order.DoesNotExist:
            raise ShopError("Order not found.", 404)

        # Проверяем статус и время УЖЕ после блокировки, а не до неё
        if order.status == Order.Status.PAID:
            raise ShopError("This order has already been paid.", 409)
        if order.status == Order.Status.CANCELLED or order.reserved_until <= timezone.now():
            raise ShopError("The reservation has expired (15 minutes). Please place the order again.", 409)

        amount = order.total
        approved, transaction_id = fake_bank(card_number, amount)

        if not approved:
            # Неудачная попытка тоже сохраняется: у заказа может быть много оплат (1:M)
            Payment.objects.create(
                order=order, transaction_id=transaction_id, amount=amount,
                status=Payment.Status.FAILED,
            )
            declined = True
        else:
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
                    raise ShopError(f"\"{item.product.product_name}\" is out of stock.", 409)

                StockLog.objects.create(
                    product_id=item.product_id,
                    changed_by="payment-system",
                    change_amount=-item.quantity,
                    reason="sale",
                )

            Payment.objects.create(
                order=order, transaction_id=transaction_id, amount=amount,
                status=Payment.Status.SUCCESS,
            )
            order.status = Order.Status.PAID
            order.save(update_fields=["status"])
    # COMMIT — выход из блока with без ошибки

    if declined:
        # Ошибку показываем уже после COMMIT, чтобы запись о неудачной попытке сохранилась
        raise ShopError("The bank declined the payment: insufficient funds. Please try another card.", 402)

    return order
@transaction.atomic
def refund_payment(payment_id, employee=None, changed_by="finance", reason="other"):
    """
    Возврат платежа одной транзакцией:
    платёж -> refunded (с причиной и временем), заказ -> cancelled,
    книги возвращаются на склад, строка в STOCK_LOG.
    Если любой шаг падает, не сохраняется ничего (ROLLBACK).
    """
    if reason not in Payment.RefundReason.values:
        raise ShopError("Please choose a refund reason.")

    try:
        # select_for_update блокирует платёж: два финансиста не вернут один платёж дважды
        payment = Payment.objects.select_for_update().get(pk=payment_id)
    except Payment.DoesNotExist:
        raise ShopError("Payment not found.", 404)

    if payment.status == Payment.Status.REFUNDED:
        raise ShopError("This payment has already been refunded.", 409)
    if payment.status != Payment.Status.SUCCESS:
        raise ShopError("Only a successful payment can be refunded.", 409)

    order = Order.objects.select_for_update().get(pk=payment.order_id)
    if order.status != Order.Status.PAID:
        raise ShopError("Only a paid order can be refunded.", 409)

    for item in order.items.select_related("product"):
        Product.objects.filter(pk=item.product_id).update(
            stock_quantity=F("stock_quantity") + item.quantity,
            last_updated=timezone.localdate(),
        )
        StockLog.objects.create(
            product_id=item.product_id,
            changed_by=changed_by,
            employee=employee,
            change_amount=item.quantity,
            reason="refund",
        )
        notify_waiting_customers(item.product_id)

    payment.status = Payment.Status.REFUNDED
    payment.refund_reason = reason
    payment.refunded_at = timezone.now()
    payment.save(update_fields=["status", "refund_reason", "refunded_at"])
    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status"])
    return payment


def notify_waiting_customers(product_id):
    """
    FR-07, критерий 4: книга снова на складе -> всем, кто нажал «Notify me», ставим notified = true.
    Покупатель увидит это на странице уведомлений (GET /api/notifications/)
    и получит письмо на email (shop/emails.py).
    Вызывается после каждого увеличения склада: админка, возврат платежа.
    Возвращает, сколько покупателей получили уведомление.
    """
    if not Product.objects.filter(pk=product_id, stock_quantity__gt=0).exists():
        return 0
    from .emails import send_back_in_stock_email  # здесь, чтобы не было циклического импорта

    waiting = list(
        StockRequest.objects.filter(product_id=product_id, notified=False).select_related("product", "customer")
    )
    StockRequest.objects.filter(pk__in=[r.pk for r in waiting]).update(
        notified=True, notified_at=timezone.now(), is_read=False
    )
    for stock_request in waiting:
        send_back_in_stock_email(stock_request)
    return len(waiting)
