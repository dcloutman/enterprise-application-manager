from rest_framework import permissions
from django.utils import timezone
from .models import UserProfile, RecordPermission


class IsApplicationAdmin(permissions.BasePermission):
    """Permission class for Application Admin users only"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            profile = request.user.profile
            return profile.role == 'application_admin'
        except UserProfile.DoesNotExist:
            return False


class CanManageUsers(permissions.BasePermission):
    """Permission class for users who can manage other users (Application Admins only)"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            profile = request.user.profile
            return profile.can_manage_users()
        except UserProfile.DoesNotExist:
            return False


class CanViewSystemNotes(permissions.BasePermission):
    """Permission class for users who can view system manager notes"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            profile = request.user.profile
            return profile.can_view_system_notes()
        except UserProfile.DoesNotExist:
            return False


class CanCreateRecords(permissions.BasePermission):
    """Permission class for users who can create new records"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            profile = request.user.profile
            return profile.can_create_records()
        except UserProfile.DoesNotExist:
            return False


class CanDeleteRecords(permissions.BasePermission):
    """Permission class for users who can delete records"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            profile = request.user.profile
            return profile.can_delete_records()
        except UserProfile.DoesNotExist:
            return False


class HasWriteAccess(permissions.BasePermission):
    """Permission class for users who have write access to records"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Allow read-only operations for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        try:
            profile = request.user.profile
            return profile.has_write_access()
        except UserProfile.DoesNotExist:
            return False


class HasRecordPermission(permissions.BasePermission):
    """Permission class to check if user has explicit permission for a specific record"""
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        try:
            profile = request.user.profile
            
            # Application Admins and Systems Managers have access to everything
            if profile.role in ['application_admin', 'systems_manager']:
                return True
            
            # For other users, check explicit permissions
            from django.contrib.contenttypes.models import ContentType
            content_type = ContentType.objects.get_for_model(obj)
            
            permission = RecordPermission.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=obj.pk
            ).first()
            
            if not permission:
                return False
            
            # Check if permission has expired
            if permission.expires_at and permission.expires_at < timezone.now():
                return False
            
            # Check permission type against request method
            if request.method in permissions.SAFE_METHODS:
                return permission.permission_type in ['read', 'write', 'full']
            elif request.method in ['POST', 'PUT', 'PATCH']:
                return permission.permission_type in ['write', 'full']
            elif request.method == 'DELETE':
                return permission.permission_type == 'full'
            
            return False
            
        except UserProfile.DoesNotExist:
            return False


class RoleBasedPermission(permissions.BasePermission):
    """
    General permission class that checks role-based permissions
    Usage: Add to view with required_roles attribute
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if view has required_roles attribute
        required_roles = getattr(view, 'required_roles', [])
        if not required_roles:
            return True  # No specific roles required
        
        try:
            profile = request.user.profile
            return profile.role in required_roles
        except UserProfile.DoesNotExist:
            return False


class CanAccessSystemNotes(permissions.BasePermission):
    """Permission class specifically for accessing system_manager_notes fields"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        try:
            profile = request.user.profile
            return profile.can_view_system_notes()
        except UserProfile.DoesNotExist:
            return False
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
