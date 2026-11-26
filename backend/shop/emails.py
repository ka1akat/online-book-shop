"""
Письма покупателям.

Как письмо уходит, решает настройка EMAIL_BACKEND (config/settings.py):
- на своём компьютере — console: письмо просто печатается в терминале, где запущен runserver;
- в тестах Django сам подменяет её на locmem: письма складываются в django.core.mail.outbox;
- на Render — BrevoEmailBackend ниже. Бесплатный Render закрывает SMTP-порты (25, 465, 587),
  поэтому письмо отправляется обычным HTTPS-запросом в Brevo (POST /v3/smtp/email).

Код магазина вызывает только стандартную функцию Django send_mail / EmailMultiAlternatives
и не знает, какой из трёх способов включён.
"""

import json
import logging
import urllib.request
from email.utils import parseaddr

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


class BrevoEmailBackend(BaseEmailBackend):
    """Свой «почтовый бэкенд» Django: вместо SMTP отправляет письмо через Brevo API."""

    def send_messages(self, email_messages):
        sent = 0
        for message in email_messages:
            try:
                self._send(message)
                sent += 1
            except Exception:
                logger.exception("Brevo: could not send e-mail to %s", message.to)
                if not self.fail_silently:
                    raise
        return sent

    def _send(self, message):
        sender_name, sender_email = parseaddr(message.from_email or settings.DEFAULT_FROM_EMAIL)
        body = {
            "sender": {"name": sender_name or "Online Book Shop", "email": sender_email},
            "to": [{"email": address} for address in message.to],
            "subject": message.subject,
            "textContent": message.body,
        }
        # HTML-версия письма, если она есть (EmailMultiAlternatives.attach_alternative)
        for content, mimetype in getattr(message, "alternatives", []):
            if mimetype == "text/html":
                body["htmlContent"] = content
        request = urllib.request.Request(
            BREVO_URL,
            data=json.dumps(body).encode(),
            headers={
                "api-key": settings.BREVO_API_KEY,
                "accept": "application/json",
                "content-type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status


def send_back_in_stock_email(stock_request):
    """FR-07+: письмо «Книга, которую вы ждали, снова в наличии». Ошибка почты не ломает склад."""
    product = stock_request.product
    customer = stock_request.customer
    book_url = f"{settings.FRONTEND_URL}/books/{product.product_id}"
    subject = f"“{product.product_name}” is back in stock"
    text = (
        f"Hello, {customer.full_name}!\n\n"
        f"Good news: the book you were waiting for is back in stock.\n\n"
        f"{product.product_name} — {product.author}\n"
        f"Price: {product.price:.0f} ₸\n\n"
        f"Order it here: {book_url}\n\n"
        f"Online Book Shop"
    )
    html = (
        f"<p>Hello, {customer.full_name}!</p>"
        f"<p>Good news: the book you were waiting for is back in stock.</p>"
        f"<p><strong>{product.product_name}</strong> — {product.author}<br>Price: {product.price:.0f} ₸</p>"
        f'<p><a href="{book_url}">Open the book and order it</a></p>'
        f"<p>Online Book Shop</p>"
    )
    message = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, [customer.email])
    message.attach_alternative(html, "text/html")
    try:
        return message.send(fail_silently=False)
    except Exception:
        logger.exception("Could not send back-in-stock e-mail to %s", customer.email)
        return 0
