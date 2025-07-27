from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import UserProfile, RecordPermission


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile with related User data"""
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    is_active = serializers.BooleanField(source='user.is_active')
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    last_login = serializers.DateTimeField(source='user.last_login', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    # Permission flags
    can_manage_users = serializers.SerializerMethodField()
    can_view_system_notes = serializers.SerializerMethodField()
    can_create_records = serializers.SerializerMethodField()
    can_delete_records = serializers.SerializerMethodField()
    has_write_access = serializers.SerializerMethodField()
    can_access_documentation = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'is_active',
            'role', 'role_display', 'department', 'phone', 'notes', 'has_documentation_access',
            'date_joined', 'last_login', 'created_at', 'updated_at',
            'can_manage_users', 'can_view_system_notes', 'can_create_records',
            'can_delete_records', 'has_write_access', 'can_access_documentation'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_can_manage_users(self, obj):
        return obj.can_manage_users()
    
    def get_can_view_system_notes(self, obj):
        return obj.can_view_system_notes()
    
    def get_can_create_records(self, obj):
        return obj.can_create_records()
    
    def get_can_delete_records(self, obj):
        return obj.can_delete_records()
    
    def get_has_write_access(self, obj):
        return obj.has_write_access()
    
    def get_can_access_documentation(self, obj):
        return obj.can_access_documentation()
    
    def update(self, instance, validated_data):
        # Update User fields
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        
        # Update UserProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users with profiles"""
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    # Profile fields
    role = serializers.ChoiceField(choices=UserProfile.USER_ROLES, default='business_user')
    department = serializers.CharField(max_length=100, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'password', 'password_confirm',
            'is_active', 'role', 'department', 'phone', 'notes'
        ]
    
    def validate(self, attrs):
        """Validate password confirmation and role permissions"""
        # Check password confirmation
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Password confirmation doesn't match")
        
        # Check if requesting user can assign this role
        request = self.context.get('request')
        if request and hasattr(request.user, 'profile'):
            requested_role = attrs.get('role', 'business_user')
            if request.user.profile.role != 'application_admin' and requested_role == 'application_admin':
                raise serializers.ValidationError("You don't have permission to create Application Admin users")
        
        return attrs
    
    def create(self, validated_data):
        # Extract profile data
        profile_data = {
            'role': validated_data.pop('role', 'business_user'),
            'department': validated_data.pop('department', ''),
            'phone': validated_data.pop('phone', ''),
            'notes': validated_data.pop('notes', ''),
        }
        
        # Remove password confirmation
        validated_data.pop('password_confirm')
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Create profile
        profile_data['user'] = user
        if hasattr(self.context.get('request'), 'user'):
            profile_data['created_by'] = self.context['request'].user
        
        UserProfile.objects.create(**profile_data)
        
        return user


class RecordPermissionSerializer(serializers.ModelSerializer):
    """Serializer for RecordPermission model"""
    username = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    granted_by_username = serializers.CharField(source='granted_by.username', read_only=True)
    content_type_name = serializers.CharField(source='content_type.name', read_only=True)
    permission_type_display = serializers.CharField(source='get_permission_type_display', read_only=True)
    
    class Meta:
        model = RecordPermission
        fields = [
            'id', 'user', 'username', 'user_full_name', 'content_type', 'content_type_name',
            'object_id', 'permission_type', 'permission_type_display', 'granted_by',
            'granted_by_username', 'granted_at', 'expires_at', 'notes'
        ]
        read_only_fields = ['id', 'granted_by', 'granted_at']
    
    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
    
    def validate_user(self, value):
        """Ensure user exists and has appropriate role for permissions"""
        if not hasattr(value, 'profile'):
            raise serializers.ValidationError("User must have a profile to receive permissions")
        
        # Only technicians and business users should receive explicit permissions
        if value.profile.role in ['application_admin', 'systems_manager']:
            raise serializers.ValidationError(
                "Application Admins and Systems Managers don't need explicit record permissions"
            )
        
        return value


class UserRoleChangeSerializer(serializers.Serializer):
    """Serializer for changing user roles"""
    role = serializers.ChoiceField(choices=UserProfile.USER_ROLES)
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_role(self, value):
        """Validate role change permissions"""
        request = self.context.get('request')
        if request and hasattr(request.user, 'profile'):
            if request.user.profile.role != 'application_admin' and value == 'application_admin':
                raise serializers.ValidationError(
                    "Only Application Admins can assign Application Admin role"
                )
        return value


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics"""
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    users_by_role = serializers.DictField()
    recent_logins = serializers.IntegerField()
    pending_permissions = serializers.IntegerField()
