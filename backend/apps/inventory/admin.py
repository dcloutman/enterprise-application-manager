from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    UserProfile, RecordPermission,
    CloudPlatform, ServerEnvironment, Language, DataStore,
    LanguageInstallation, DataStoreInstance, Application,
    ApplicationLanguageDependency, ApplicationDataStoreDependency,
    ApplicationLifecycleEvent, CloudPlugin
)


@admin.register(CloudPlatform)
class CloudPlatformAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'plugin_enabled', 'created_at']
    list_filter = ['is_active', 'plugin_enabled']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ServerEnvironment)
class ServerEnvironmentAdmin(admin.ModelAdmin):
    list_display = ['hostname', 'ip_address', 'operating_system', 'environment_type', 'is_active']
    list_filter = ['environment_type', 'operating_system', 'is_active', 'cloud_platform']
    search_fields = ['hostname', 'ip_address', 'name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'hostname', 'ip_address', 'environment_type')
        }),
        ('System Information', {
            'fields': ('operating_system', 'os_version')
        }),
        ('Cloud Configuration', {
            'fields': ('cloud_platform', 'cloud_instance_id', 'cloud_region'),
            'classes': ['collapse']
        }),
        ('Hardware Specifications', {
            'fields': ('cpu_cores', 'memory_gb', 'storage_gb'),
            'classes': ['collapse']
        }),
        ('Status & Notes', {
            'fields': ('is_active', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DataStore)
class DataStoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'datastore_type', 'is_active', 'created_at']
    list_filter = ['datastore_type', 'is_active']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LanguageInstallation)
class LanguageInstallationAdmin(admin.ModelAdmin):
    list_display = ['language', 'version', 'server', 'is_default', 'created_at']
    list_filter = ['language', 'is_default', 'server__environment_type']
    search_fields = ['language__name', 'version', 'server__hostname']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DataStoreInstance)
class DataStoreInstanceAdmin(admin.ModelAdmin):
    list_display = ['datastore', 'instance_name', 'version', 'server', 'port', 'is_active']
    list_filter = ['datastore', 'is_active', 'server__environment_type']
    search_fields = ['datastore__name', 'instance_name', 'server__hostname']
    readonly_fields = ['created_at', 'updated_at']


class ApplicationLanguageDependencyInline(admin.TabularInline):
    model = ApplicationLanguageDependency
    extra = 1
    fields = ['language_installation', 'is_primary', 'notes']


class ApplicationDataStoreDependencyInline(admin.TabularInline):
    model = ApplicationDataStoreDependency
    extra = 1
    fields = ['datastore_instance', 'is_primary', 'connection_type', 'notes']


class ApplicationLifecycleEventInline(admin.TabularInline):
    model = ApplicationLifecycleEvent
    extra = 0
    readonly_fields = ['from_stage', 'to_stage', 'event_date', 'performed_by']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'lifecycle_stage', 'criticality', 'primary_server', 'business_owner', 'is_active']
    list_filter = ['lifecycle_stage', 'criticality', 'is_active', 'uses_ldap', 'primary_server__environment_type']
    search_fields = ['name', 'business_owner', 'technical_owner', 'primary_server__hostname']
    readonly_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
    inlines = [ApplicationLanguageDependencyInline, ApplicationDataStoreDependencyInline, ApplicationLifecycleEventInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'business_purpose', 'version')
        }),
        ('Lifecycle Management', {
            'fields': ('lifecycle_stage', 'criticality')
        }),
        ('Ownership', {
            'fields': ('business_owner', 'technical_owner')
        }),
        ('Infrastructure', {
            'fields': ('primary_server', 'additional_servers', 'deployment_path')
        }),
        ('Authentication', {
            'fields': ('uses_ldap', 'ldap_config'),
            'classes': ['collapse']
        }),
        ('Status & Notes', {
            'fields': ('is_active', 'notes')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ['collapse']
        })
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        
        # Track lifecycle changes
        if change and 'lifecycle_stage' in form.changed_data:
            original = Application.objects.get(pk=obj.pk)
            ApplicationLifecycleEvent.objects.create(
                application=obj,
                from_stage=original.lifecycle_stage,
                to_stage=obj.lifecycle_stage,
                performed_by=request.user
            )
        
        super().save_model(request, obj, form, change)


@admin.register(ApplicationLanguageDependency)
class ApplicationLanguageDependencyAdmin(admin.ModelAdmin):
    list_display = ['application', 'language_installation', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'language_installation__language']
    search_fields = ['application__name', 'language_installation__language__name']


@admin.register(ApplicationDataStoreDependency)
class ApplicationDataStoreDependencyAdmin(admin.ModelAdmin):
    list_display = ['application', 'datastore_instance', 'is_primary', 'connection_type', 'created_at']
    list_filter = ['is_primary', 'connection_type', 'datastore_instance__datastore']
    search_fields = ['application__name', 'datastore_instance__datastore__name']


@admin.register(ApplicationLifecycleEvent)
class ApplicationLifecycleEventAdmin(admin.ModelAdmin):
    list_display = ['application', 'from_stage', 'to_stage', 'event_date', 'performed_by']
    list_filter = ['from_stage', 'to_stage', 'event_date']
    search_fields = ['application__name', 'performed_by__username']
    readonly_fields = ['event_date']


@admin.register(CloudPlugin)
class CloudPluginAdmin(admin.ModelAdmin):
    list_display = ['name', 'cloud_platform', 'version', 'is_enabled', 'created_at']
    list_filter = ['cloud_platform', 'is_enabled']
    search_fields = ['name', 'plugin_module']
    readonly_fields = ['created_at', 'updated_at']


class UserProfileInline(admin.StackedInline):
    """Inline UserProfile editor for User admin"""
    model = UserProfile
    fk_name = 'user'  # Specify which ForeignKey to use
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['role', 'is_active', 'has_documentation_access', 'department', 'phone', 'notes']
    
    def get_readonly_fields(self, request, obj=None):
        readonly = ['created_at', 'updated_at']
        # Only Application Admins can modify documentation access for non-admins
        if not request.user.is_superuser and hasattr(request.user, 'profile'):
            if request.user.profile.role != 'application_admin':
                readonly.append('has_documentation_access')
        return readonly


class CustomUserAdmin(BaseUserAdmin):
    """Extended User admin with UserProfile inline"""
    inlines = (UserProfileInline,)
    
    def get_inline_instances(self, request, obj=None):
        # Ensure UserProfile exists for all users
        if obj and not hasattr(obj, 'profile'):
            UserProfile.objects.create(user=obj)
        return super().get_inline_instances(request, obj)


# Re-register User admin with our custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Direct UserProfile admin for advanced management"""
    list_display = ['user', 'role', 'department', 'is_active', 'has_documentation_access', 'created_at']
    list_filter = ['role', 'is_active', 'has_documentation_access', 'department']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'department']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Role and Permissions', {
            'fields': ('role', 'is_active', 'has_documentation_access')
        }),
        ('Contact Information', {
            'fields': ('department', 'phone')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly = ['created_at', 'updated_at']
        # Only Application Admins can modify documentation access for non-admins
        if not request.user.is_superuser and hasattr(request.user, 'profile'):
            if request.user.profile.role != 'application_admin':
                readonly.append('has_documentation_access')
        return readonly
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new profile
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(RecordPermission)
class RecordPermissionAdmin(admin.ModelAdmin):
    """Admin for managing record-level permissions"""
    list_display = ['user', 'content_type', 'permission_type', 'granted_by', 'granted_at', 'expires_at']
    list_filter = ['permission_type', 'content_type', 'granted_at', 'expires_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'granted_by__username']
    readonly_fields = ['granted_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Creating new permission
            obj.granted_by = request.user
        super().save_model(request, obj, form, change)
