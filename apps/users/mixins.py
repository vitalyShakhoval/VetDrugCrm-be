from rest_framework.exceptions import PermissionDenied
from rolepermissions.checkers import has_role, has_permission

class RoleRequiredMixin:
    required_role_class = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        
        if not self.required_role_class:
            raise ValueError("required_role_class должен быть задан")
        
        if not has_role(request.user, self.required_role_class):
            raise PermissionDenied(
                f"Доступ запрещен. Требуется роль: {self.required_role_class.__name__}"
            )

class PermissionRequiredMixin:
    required_permission = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        
        if not self.required_permission:
            raise ValueError("required_permission должен быть задан")

        if not has_permission(request.user, self.required_permission):
            raise PermissionDenied(
                f"Доступ запрещен. Требуется право: {self.required_permission}"
            )