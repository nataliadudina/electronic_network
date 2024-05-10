from rest_framework import permissions


class IsActive(permissions.BasePermission):
    """
    Проверяет, является ли пользователь активным.
    """

    def has_permission(self, request, view):
        return request.user.is_active
