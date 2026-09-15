from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import User


class IsAdmin(BasePermission):
    message = "Administrator access is required."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == User.Role.ADMIN)


class IsStudent(BasePermission):
    message = "Student access is required."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == User.Role.STUDENT)


class IsSupervisor(BasePermission):
    message = "Supervisor access is required."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == User.Role.SUPERVISOR)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.method in SAFE_METHODS or request.user.role == User.Role.ADMIN


class IsSelfOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = getattr(obj, "user", obj)
        return request.user.role == User.Role.ADMIN or user == request.user


class IsPlacementStudent(BasePermission):
    message = "You can only access your own placement records."

    def has_object_permission(self, request, view, obj):
        placement = getattr(obj, "placement", obj)
        return placement.student.user_id == request.user.id


class IsAssignedSupervisor(BasePermission):
    message = "Only the assigned supervisor can access this record."

    def has_object_permission(self, request, view, obj):
        placement = getattr(obj, "placement", obj)
        return placement.supervisor.user_id == request.user.id
