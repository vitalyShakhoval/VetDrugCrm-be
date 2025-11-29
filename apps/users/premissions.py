from rest_framework import permissions

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authentificated and request.user.is_manager()
    
class IsWarehouseSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authentificated and request.user.is_warehouse_supervisor()

class IsVeterinarian(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authentificated and request.user.is_veterinarian()

