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


class HasRole(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        return get_role(request.user) in self.allowed_roles + ["admin"]


class IsWarehouse(HasRole):
    allowed_roles = ["warehouse"]