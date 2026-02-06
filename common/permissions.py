from rest_framework import (
    permissions,
)


class AlwaysDeny(permissions.BasePermission):
    """Всегда возвращает 403 — только для тестирования"""

    def has_permission(self, request, view):  # type: ignore
        return False

    def has_object_permission(self, request, view, obj):  # type: ignore
        return False
