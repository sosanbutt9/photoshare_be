from rest_framework import permissions

from accounts.models import User


class IsAdminUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (getattr(user, "role", None) == User.Role.ADMIN or user.is_superuser)
        )


class IsCreatorUser(permissions.BasePermission):
    """Creators may upload; admins and Django superusers may as well."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        role = getattr(user, "role", None)
        return bool(
            role == User.Role.CREATOR
            or role == User.Role.ADMIN
            or user.is_superuser
        )


class IsConsumerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == User.Role.CONSUMER
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object owner is `creator` (e.g. Photo) or `author` (e.g. Comment), or admin.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "role", None) == User.Role.ADMIN or user.is_superuser:
            return True
        owner = getattr(obj, "creator", None) or getattr(obj, "author", None)
        return owner == user


class IsCreatorOwnerOrAdmin(permissions.BasePermission):
    """Creator role and owns the object, or admin."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "role", None) == User.Role.ADMIN or user.is_superuser:
            return True
        if getattr(user, "role", None) != User.Role.CREATOR:
            return False
        creator = getattr(obj, "creator", None)
        return creator == user
