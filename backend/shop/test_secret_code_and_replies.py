"""Тесты: секретный код заказа, проверка текста обращения, ответы поддержки и «Мои обращения»."""

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Customer, Employee, Order, SupportTicket
from .moderation import check_support_message
from .views import make_token

SUPPORT_URL = "/api/support/"
GOOD_TEXT = "My parcel has not arrived yet, please check the delivery."


def make_order(customer, status="paid"):
    return Order.objects.create(
        customer=customer, status=status, reserved_until=timezone.now() + timedelta(minutes=15)
    )


class SecretOrderCodeTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.customer = Customer.objects.create(full_name="Aidar Nurlanov", email="aidar@example.com")
        self.order = make_order(self.customer, status="reserved")

    def test_every_order_gets_its_own_random_code(self):
        other = make_order(self.customer)
        self.assertNotEqual(self.order.public_code, other.public_code)
        self.assertIsInstance(self.order.public_code, uuid.UUID)

    def test_order_opens_by_secret_code(self):
        r = self.client.get(f"/api/orders/{self.order.public_code}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["order_id"], self.order.order_id)
        self.assertEqual(r.data["public_code"], str(self.order.public_code))

    def test_order_does_not_open_by_plain_number(self):
        # Главное: номера идут подряд, поэтому по номеру чужой заказ подобрать было бы легко
        self.assertEqual(self.client.get(f"/api/orders/{self.order.order_id}/").status_code, 404)
        r = self.client.post(f"/api/orders/{self.order.order_id}/pay/", {"card_number": "4111111111111111"}, format="json")
        self.assertEqual(r.status_code, 404)

    def test_unknown_code_gives_404(self):
        self.assertEqual(self.client.get(f"/api/orders/{uuid.uuid4()}/").status_code, 404)

    def test_pay_by_secret_code_works(self):
        r = self.client.post(f"/api/orders/{self.order.public_code}/pay/", {"card_number": "4111111111111111"}, format="json")
        # заказ без позиций оплатить нельзя, но до заказа запрос дошёл: это не 404 «заказ не найден»
        self.assertNotEqual(r.data.get("detail"), "Order not found.")


class SupportByCodeAndModerationTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.customer = Customer.objects.create(full_name="Aidar Nurlanov", email="aidar@example.com")
        self.order = make_order(self.customer)

    def send(self, **overrides):
        body = {"order_code": str(self.order.public_code), "topic": "delivery", "message": GOOD_TEXT}
        body.update(overrides)
        return self.client.post(SUPPORT_URL, body, format="json")

    def test_secret_code_needs_no_email(self):
        r = self.send()
        self.assertEqual(r.status_code, 201)
        self.assertEqual(SupportTicket.objects.get().order, self.order)

    def test_unknown_code_is_rejected(self):
        r = self.send(order_code=str(uuid.uuid4()))
        self.assertEqual(r.status_code, 404)
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_order_is_required(self):
        r = self.client.post(SUPPORT_URL, {"topic": "other", "message": GOOD_TEXT}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_rude_message_is_not_saved(self):
        for text in ("ты идиот, сайт говно", "this is shit service, fuck you", "это х у й н я полная"):
            r = self.send(message=text)
            self.assertEqual(r.status_code, 400, text)
            self.assertIn("detail", r.data)
        self.assertEqual(SupportTicket.objects.count(), 0)  # в базу ничего не попало

    def test_links_and_nonsense_are_not_saved(self):
        for text in ("buy now https://spam.example.com", "write to t.me/spamchannel", "aaaaaaaaaaaa", "12345 !!! ???"):
            self.assertEqual(self.send(message=text).status_code, 400, text)
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_normal_messages_pass(self):
        normal = [
            "Здравствуйте, мой заказ не пришёл, прошло уже 5 дней.",
            "Курьер не позвонил в домофон, квартира 12, подъезд 3",
            "Менің тапсырысым келмеді, көмектесіңіз",
            "Скотт Фицджеральд, небанальный сюжет, хлеб и себе на карту",
        ]
        for text in normal:
            self.assertIsNone(check_support_message(text), text)
        self.assertEqual(self.send(message=normal[0]).status_code, 201)

    def test_rude_text_is_checked_before_order_lookup(self):
        # даже с неверным кодом сначала проверяется текст, чтобы мусор не обрабатывался дальше
        r = self.send(order_code=str(uuid.uuid4()), message="Ты идиот, где мой заказ?")
        self.assertEqual(r.status_code, 400)

    def test_empty_and_too_short_messages_get_clear_explanations(self):
        for text, part in (("", "empty"), ("      \n  ", "empty"), ("help me", "too short")):
            r = self.send(message=text)
            self.assertEqual(r.status_code, 400, text)
            self.assertIn(part, r.data["detail"])
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_minimum_is_ten_characters(self):
        self.assertEqual(self.send(message="Book lost.").status_code, 201)  # ровно 10 символов
        self.assertEqual(self.send(message="Book lost").status_code, 400)  # 9 символов

    def test_repeated_word_is_spam(self):
        r = self.send(message="buy buy buy buy buy buy now")
        self.assertEqual(r.status_code, 400)
        self.assertIn("spam", r.data["detail"])
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_more_rude_words_are_blocked(self):
        for text in (
            "Вы меня наебали с этим заказом",
            "This shop is shitty and the delivery is late",
            "Вы все идиоты, верните деньги за заказ",
            "Ақымақ сайт, жұмыс істемейді",
            "Какой пиздец с этой доставкой",
        ):
            self.assertEqual(self.send(message=text).status_code, 400, text)
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_words_that_only_look_rude_pass(self):
        # слова-ловушки: внутри есть «еб», «хуй» и т.п., но грубыми они не являются
        for text in (
            "Я купил хлеб и книгу, но заказ не пришёл вовремя",
            "Доставка задерживается, небо уже серое, а книги нет",
            "Курьер сказал, что требует подтверждения заказа",
            "I paid twice for the same book, please refund one payment.",
            "Please tell me the price. It was 4500 ₸ and then 5000 ₸ at payment.",
        ):
            self.assertIsNone(check_support_message(text), text)
            self.assertEqual(self.send(message=text).status_code, 201, text)

    def test_saved_message_has_no_spaces_around(self):
        self.send(message="   Where is my parcel, please?   ")
        self.assertEqual(SupportTicket.objects.get().message, "Where is my parcel, please?")


class TicketRepliesTests(APITestCase):
    def setUp(self):
        cache.clear()
        user_model = get_user_model()
        self.aidar = Customer.objects.create(full_name="Aidar Nurlanov", email="aidar@example.com")
        self.dana = Customer.objects.create(full_name="Dana Sarsen", email="dana@example.com")
        self.aidar_user = user_model.objects.create_user("aidar@example.com", email="aidar@example.com", password="x")
        self.dana_user = user_model.objects.create_user("dana@example.com", email="dana@example.com", password="x")
        self.aidar_order = make_order(self.aidar)
        self.dana_order = make_order(self.dana)
        self.ticket = SupportTicket.objects.create(
            order=self.aidar_order, customer=self.aidar, topic="refund", message="Please refund this order.")
        self.other_ticket = SupportTicket.objects.create(
            order=self.dana_order, customer=self.dana, topic="delivery", message="Where is my parcel?")

    def login_as(self, role):
        user = get_user_model().objects.create_user(role, password="x", is_staff=True)
        Employee.objects.create(user=user, role=role)
        self.client.force_login(user)
        return user

    def reply_in_admin(self, text="We have refunded the money.", status="open"):
        return self.client.post(
            f"/admin/shop/supportticket/{self.ticket.pk}/change/",
            {"status": status, "staff_reply": text},
        )

    # --- сотрудник пишет ответ ---
    def test_support_can_write_a_reply(self):
        user = self.login_as("support")
        r = self.reply_in_admin()
        self.assertEqual(r.status_code, 302, getattr(r, "context", None) and r.context["adminform"].form.errors)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.staff_reply, "We have refunded the money.")
        self.assertIsNotNone(self.ticket.replied_at)
        self.assertEqual(self.ticket.handled_by.user, user)
        self.assertEqual(self.ticket.status, "in_progress")  # открытое обращение с ответом стало «в работе»

    def test_manager_and_finance_cannot_write_a_reply(self):
        for role in ("manager", "finance"):
            self.login_as(role)
            self.assertEqual(self.reply_in_admin().status_code, 403)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.staff_reply, "")

    def test_customer_text_cannot_be_changed_by_reply_form(self):
        self.login_as("support")
        self.client.post(f"/admin/shop/supportticket/{self.ticket.pk}/change/",
                         {"status": "open", "staff_reply": "ok reply", "message": "hacked text"})
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.message, "Please refund this order.")

    # --- покупатель видит ответ ---
    def reply(self):
        self.ticket.staff_reply = "We have refunded the money."
        self.ticket.replied_at = timezone.now()
        self.ticket.save()

    def auth(self, user):
        return {"HTTP_AUTHORIZATION": f"Bearer {make_token(user)}"}

    def test_my_tickets_needs_login(self):
        self.assertEqual(self.client.get("/api/my-tickets/").status_code, 401)

    def test_my_tickets_shows_only_own_tickets_with_reply(self):
        self.reply()
        r = self.client.get("/api/my-tickets/", **self.auth(self.aidar_user))
        self.assertEqual(r.status_code, 200)
        self.assertEqual([t["ticket_id"] for t in r.data], [self.ticket.ticket_id])
        self.assertEqual(r.data[0]["staff_reply"], "We have refunded the money.")
        # чужое не попадает
        r = self.client.get("/api/my-tickets/", **self.auth(self.dana_user))
        self.assertEqual([t["ticket_id"] for t in r.data], [self.other_ticket.ticket_id])
        self.assertEqual(r.data[0]["staff_reply"], "")

    def test_staff_details_are_not_shown_to_customer(self):
        self.reply()
        r = self.client.get("/api/my-tickets/", **self.auth(self.aidar_user))
        self.assertNotIn("handled_by", r.data[0])
        self.assertNotIn("customer", r.data[0])

    def test_order_tickets_by_secret_code_show_only_that_order(self):
        self.reply()
        r = self.client.get(f"/api/orders/{self.aidar_order.public_code}/tickets/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual([t["ticket_id"] for t in r.data], [self.ticket.ticket_id])
        self.assertEqual(r.data[0]["staff_reply"], "We have refunded the money.")

    def test_order_tickets_by_number_or_wrong_code_do_not_work(self):
        self.reply()
        self.assertEqual(self.client.get(f"/api/orders/{self.aidar_order.order_id}/tickets/").status_code, 404)
        self.assertEqual(self.client.get(f"/api/orders/{uuid.uuid4()}/tickets/").status_code, 404)
