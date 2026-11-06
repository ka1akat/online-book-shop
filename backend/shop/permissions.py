from rest_framework.permissions import BasePermission
from .models import Employee


def get_role(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return "admin"
    emp = Employee.objects.filter(user=user).first()
    return emp.role if emp else None


class RoleAdminMixin:
    view_roles = []   # кто может смотреть
    edit_roles = []   # кто может менять, добавлять, удалять

    def has_module_permission(self, request):
        return get_role(request.user) in self.view_roles + self.edit_roles + ["admin"]

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def _can_edit(self, request):
        return get_role(request.user) in self.edit_roles + ["admin"]

    def has_add_permission(self, request, obj=None):
        return self._can_edit(request)

    def has_change_permission(self, request, obj=None):
        return self._can_edit(request)

    def has_delete_permission(self, request, obj=None):
        return self._can_edit(request)


def permissions_for_role(role):
    """
    Какие стандартные разрешения Django соответствуют роли.
    Берётся из тех же view_roles / edit_roles, что и в admin.py, поэтому
    правила описаны в одном месте. Используется, чтобы после выбора роли
    в окне «User permissions» были выбраны нужные разрешения.
    """
    from django.contrib import admin
    from django.contrib.auth.models import Permission

    codenames = set()

    def collect(model, view_roles, edit_roles):
        name = model._meta.model_name
        if role == "admin" or role in view_roles or role in edit_roles:
            codenames.add(f"view_{name}")
        if role == "admin" or role in edit_roles:
            codenames.update({f"add_{name}", f"change_{name}", f"delete_{name}"})

    for model, model_admin in admin.site._registry.items():
        if isinstance(model_admin, RoleAdminMixin):
            collect(model, model_admin.view_roles, model_admin.edit_roles)
        for inline in getattr(model_admin, "inlines", []):
            if issubclass(inline, RoleAdminMixin):
                collect(inline.model, inline.view_roles, inline.edit_roles)

    return Permission.objects.filter(
        content_type__app_label="shop", codename__in=codenames
    )


class HasRole(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        return get_role(request.user) in self.allowed_roles + ["admin"]


class IsWarehouse(HasRole):
    allowed_roles = ["warehouse"]


class IsWarehouseOrManager(HasRole):
    allowed_roles = ["warehouse", "manager"]