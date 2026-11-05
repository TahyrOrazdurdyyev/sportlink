"""
Custom permissions for MongoDB project
"""
from rest_framework.permissions import BasePermission
from apps.users.models import User


class IsAdminUser(BasePermission):
    """Permission for admin users only"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            hasattr(request.user, 'is_staff') and
            request.user.is_staff
        )


class IsOwnerOrReadOnly(BasePermission):
    """Permission to only allow owners to edit objects"""
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Write permissions only to the owner
        return obj.user == request.user


class IsActiveUser(BasePermission):
    """Permission for active users only"""
    
    def has_permission(self, request, view):
        return (
            request.user and
            hasattr(request.user, 'is_active') and
            request.user.is_active and
            not getattr(request.user, 'is_banned', False)
        )