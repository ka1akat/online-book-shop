"""Правило бесплатной доставки.

Если сумма книг в заказе БОЛЬШЕ 10 000 тенге, доставка бесплатная.
Заказ ровно на 10 000 платит за доставку (слово «превышает» значит «строго больше»).
Если скажут «от 10 000», замени в функции знак > на >=.
Сами тарифы доставки (по городу, за город) остаются в Order.delivery_fee в models.py.
"""
from decimal import Decimal

FREE_DELIVERY_THRESHOLD = Decimal("10000")  # порог, тенге


def is_free_delivery(items_total):
    """True, если сумма книг превышает порог бесплатной доставки."""
    return Decimal(items_total) > FREE_DELIVERY_THRESHOLD