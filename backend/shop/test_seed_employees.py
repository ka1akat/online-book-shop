from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from .models import Employee


def seed(**options):
    call_command("seed_employees", stdout=StringIO(), **options)


class SeedEmployeesTests(TestCase):
    def test_creates_one_employee_per_role(self):
        seed(password="Demo-pass-1")
        roles = set(Employee.objects.values_list("role", flat=True))
        self.assertEqual(roles, {"warehouse", "finance", "support", "manager", "admin"})
        self.assertEqual(Employee.objects.count(), 5)

    def test_demo_employees_can_log_in_and_get_staff_access(self):
        seed(password="Demo-pass-1")
        user = get_user_model().objects.get(username="demo_warehouse")
        self.assertTrue(user.check_password("Demo-pass-1"))
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.user_permissions.filter(codename="change_product").exists())
        self.assertFalse(user.user_permissions.filter(codename="view_payment").exists())

    def test_admin_is_superuser(self):
        seed(password="Demo-pass-1")
        self.assertTrue(get_user_model().objects.get(username="demo_admin").is_superuser)

    def test_running_twice_does_not_duplicate_and_keeps_passwords(self):
        seed(password="Demo-pass-1")
        seed(password="Another-pass-2")
        self.assertEqual(Employee.objects.count(), 5)
        user = get_user_model().objects.get(username="demo_finance")
        self.assertTrue(user.check_password("Demo-pass-1"))  # без --reset пароль не меняется

    def test_reset_changes_password(self):
        seed(password="Demo-pass-1")
        seed(password="Another-pass-2", reset=True)
        user = get_user_model().objects.get(username="demo_finance")
        self.assertTrue(user.check_password("Another-pass-2"))

    def test_random_passwords_differ_when_not_given(self):
        seed()
        users = get_user_model().objects.filter(username__startswith="demo_")
        hashes = {u.password for u in users}
        self.assertEqual(len(hashes), 5)