import secrets

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from shop.models import Employee

ROLES = ["warehouse", "finance", "support", "manager", "admin"]


class Command(BaseCommand):
    help = "Создаёт демо-сотрудников: по одному на каждую роль (для показа админки)."

    def add_arguments(self, parser):
        parser.add_argument("--password", help="Один пароль для всех демо-сотрудников (по умолчанию у каждого свой случайный)")
        parser.add_argument("--reset", action="store_true", help="Сбросить пароли уже существующим демо-сотрудникам")

    def handle(self, *args, **options):
        User = get_user_model()
        rows = []
        for role in ROLES:
            username = f"demo_{role}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": "Demo", "last_name": role.capitalize()},
            )
            password = None
            if created or options["reset"]:
                password = options["password"] or secrets.token_urlsafe(9)
                user.set_password(password)
            if role == "admin":
                user.is_superuser = True  # админ может создавать пользователей и менять роли
            user.is_staff = True
            user.is_active = True
            user.save()
            # Employee.save() сам выдаёт доступ в админку и разрешения по роли
            Employee.objects.update_or_create(user=user, defaults={"role": role})
            rows.append((username, role, password or "(пароль не менялся)"))

        self.stdout.write(self.style.SUCCESS("Демо-сотрудники готовы:"))
        for username, role, password in rows:
            self.stdout.write(f"  {role:<10} login: {username:<15} password: {password}")
        self.stdout.write("Только для демонстрации: не используйте эти аккаунты на настоящем сайте.")