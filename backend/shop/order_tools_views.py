"""Адрес API: отмена брони покупателем."""
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .cancellation import cancel_order
from .services import ShopError


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class CancelOrderView(APIView):
    """POST /api/orders/<id>/cancel/  с телом {"email": "..."}  (покупатель снимает бронь)."""

    # Вход в аккаунт не нужен: принадлежность заказа проверяется по email покупателя
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, order_id):
        form = EmailSerializer(data=request.data)
        form.is_valid(raise_exception=True)
        try:
            order = cancel_order(order_id, form.validated_data["email"])
        except ShopError as e:
            return Response({"detail": e.message}, status=e.status_code)
        return Response({
            "order_id": order.order_id,
            "status": order.status,
            "detail": "Бронь отменена, книги снова доступны для покупки.",
        })