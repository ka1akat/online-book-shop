from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Customer, Employee, Order, SupportTicket
from .views import SupportThrottle, make_token

URL = "/api/support/"


class SupportApiTests(APITestCase):
    def setUp(self):
        cache.clear()  # счётчик ограничения запросов не должен переходить из теста в тест
        self.customer = Customer.objects.create(full_name="Aidar Nurlanov", email="aidar@example.com")
        self.order = Order.objects.create(
            customer=self.customer, status="paid", reserved_until=timezone.now() + timedelta(minutes=15)
        )
        Customer.objects.create(full_name="Dana Sarsen", email="dana@example.com")

    def send(self, **overrides):
        body = {"order_id": self.order.order_id, "email": "aidar@example.com",
                "topic": "refund", "message": "I changed my mind about this book."}
        body.update(overrides)
        return self.client.post(URL, body, format="json")

    def test_valid_request_creates_open_ticket(self):
        r = self.send()
        self.assertEqual(r.status_code, 201)
        ticket = SupportTicket.objects.get()
        self.assertEqual((ticket.status, ticket.topic), ("open", "refund"))
        self.assertEqual(ticket.customer, self.customer)  # покупатель берётся из заказа
        self.assertEqual(r.data["ticket_id"], ticket.ticket_id)

    def test_email_is_case_insensitive(self):
        self.assertEqual(self.send(email="Aidar@Example.COM").status_code, 201)

    def test_someone_elses_order_is_rejected_without_creating_a_ticket(self):
        r = self.send(email="dana@example.com")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_missing_order_and_foreign_order_give_the_same_answer(self):
        foreign = self.send(email="dana@example.com")
        missing = self.send(order_id=99999)
        self.assertEqual(foreign.status_code, missing.status_code)
        self.assertEqual(foreign.data["detail"], missing.data["detail"])  # нельзя узнать, есть ли чужой заказ

    def test_anonymous_without_email_is_rejected(self):
        r = self.send(email="")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_message_and_topic_are_validated(self):
        self.assertEqual(self.send(message="hi").status_code, 400)  # слишком короткое
        self.assertEqual(self.send(message="     ").status_code, 400)  # одни пробелы
        self.assertEqual(self.send(topic="spam").status_code, 400)  # темы нет в списке
        self.assertEqual(SupportTicket.objects.count(), 0)

    def test_logged_in_customer_is_identified_by_token_not_by_email_in_body(self):
        owner = get_user_model().objects.create_user("aidar@example.com", email="aidar@example.com", password="x")
        stranger = get_user_model().objects.create_user("dana@example.com", email="dana@example.com", password="x")
        # владелец заказа: email в теле можно не присылать
        r = self.client.post(URL, {"order_id": self.order.order_id, "topic": "delivery", "message": "Where is my parcel?"},
                             format="json", HTTP_AUTHORIZATION=f"Bearer {make_token(owner)}")
        self.assertEqual(r.status_code, 201)
        # чужой токен + email владельца в теле: заказ всё равно не отдаётся
        r = self.client.post(URL, {"order_id": self.order.order_id, "email": "aidar@example.com",
                                   "topic": "delivery", "message": "Where is my parcel?"},
                             format="json", HTTP_AUTHORIZATION=f"Bearer {make_token(stranger)}")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(SupportTicket.objects.count(), 1)

    def test_too_many_requests_are_throttled(self):
        with patch.object(SupportThrottle, "rate", "2/hour"):
            self.assertEqual(self.send().status_code, 201)
            self.assertEqual(self.send().status_code, 201)
            self.assertEqual(self.send().status_code, 429)  # защита от спама
        self.assertEqual(SupportTicket.objects.count(), 2)

    def test_database_rejects_unknown_status(self):
        self.send()
        with self.assertRaises(IntegrityError), transaction.atomic():
            SupportTicket.objects.update(status="weird")  # CHECK в таблице


class SupportAdminTests(APITestCase):
    def setUp(self):
        cache.clear()
        customer = Customer.objects.create(full_name="Aidar Nurlanov", email="aidar@example.com")
        order = Order.objects.create(customer=customer, status="paid",
                                     reserved_until=timezone.now() + timedelta(minutes=15))
        self.refund = SupportTicket.objects.create(order=order, customer=customer, topic="refund",
                                                   message="Please refund this order.")
        self.delivery = SupportTicket.objects.create(order=order, customer=customer, topic="delivery",
                                                     message="Where is my parcel?")

    def login_as(self, role):
        user = get_user_model().objects.create_user(role, password="x", is_staff=True)
        Employee.objects.create(user=user, role=role)
        self.client.force_login(user)
        return user

    def list_tickets(self):
        r = self.client.get("/admin/shop/supportticket/")
        return r, r.context["cl"].result_list if r.status_code == 200 else []

    def act(self, action, *tickets):
        return self.client.post("/admin/shop/supportticket/", {
            "action": action, "_selected_action": [t.pk for t in tickets], "index": 0,
        })

    def test_support_sees_all_tickets(self):
        self.login_as("support")
        r, tickets = self.list_tickets()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(tickets), 2)

    def test_finance_sees_only_refund_tickets(self):
        self.login_as("finance")
        r, tickets = self.list_tickets()
        self.assertEqual(r.status_code, 200)
        self.assertEqual([t.topic for t in tickets], ["refund"])
        # прямая ссылка на чужое по теме обращение тоже не открывается
        self.assertEqual(self.client.get(f"/admin/shop/supportticket/{self.delivery.pk}/change/").status_code, 302)

    def test_warehouse_cannot_open_tickets(self):
        self.login_as("warehouse")
        self.assertEqual(self.client.get("/admin/shop/supportticket/").status_code, 403)

    def test_support_takes_ticket_in_work_and_closes_it(self):
        user = self.login_as("support")
        self.act("take_in_work", self.refund)
        self.refund.refresh_from_db()
        self.assertEqual(self.refund.status, "in_progress")
        self.assertEqual(self.refund.handled_by.user, user)
        self.act("close_selected", self.refund)
        self.refund.refresh_from_db()
        self.assertEqual(self.refund.status, "closed")
        self.assertIsNotNone(self.refund.closed_at)

    def test_manager_and_finance_cannot_close_tickets(self):
        for role in ("manager", "finance"):
            self.login_as(role)
            self.act("close_selected", self.refund)
        self.refund.refresh_from_db()
        self.assertEqual(self.refund.status, "open")

    def test_nobody_can_add_or_delete_tickets_in_admin(self):
        self.login_as("support")
        self.assertEqual(self.client.get("/admin/shop/supportticket/add/").status_code, 403)
        self.client.post("/admin/shop/supportticket/", {
            "action": "delete_selected", "_selected_action": [self.refund.pk], "index": 0, "post": "yes",
        })
        self.assertTrue(SupportTicket.objects.filter(pk=self.refund.pk).exists())