"""Отмена брони покупателем."""
from django.db import transaction

from .models import Order
from .services import ShopError, expire_reservations


def cancel_order(order_id, email):
    """Покупатель сам снимает бронь своего заказа.

    1. Снимаем просроченные брони (как в pay_order).
    2. Блокируем строку заказа, чтобы отмена и оплата не прошли одновременно.
    3. Проверяем, что заказ принадлежит этому email (иначе «не найден»).
    4. Отменить можно только заказ в статусе reserved.
    5. Ставим статус cancelled. Склад не меняем: при брони он и не уменьшался,
       а свободное количество считается только по броням в статусе reserved,
       поэтому книги освобождаются автоматически.
    """
    expire_reservations()
    email = (email or "").strip().lower()

    with transaction.atomic():
        try:
            order = Order.objects.select_for_update().get(pk=order_id)
        except Order.DoesNotExist:
            raise ShopError("Заказ не найден.", 404)

        # Чужой заказ отвечаем так же, как несуществующий: не раскрываем, что он есть
        if order.customer.email.lower() != email:
            raise ShopError("Заказ не найден.", 404)

        if order.status == Order.Status.PAID:
            raise ShopError("Заказ уже оплачен, отменить бронь нельзя.", 409)
        if order.status == Order.Status.CANCELLED:
            raise ShopError("Заказ уже отменён (или бронь истекла).", 409)

        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status"])

    return order