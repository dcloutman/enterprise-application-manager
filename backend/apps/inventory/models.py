from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from .audit_signals import AuditMixin
import uuid


class UserProfile(AuditMixin, models.Model):
    """Extended user profile with role-based access control"""
    USER_ROLES = [
        ('application_admin', 'Application Admin'),
        ('systems_manager', 'Systems Manager'),
        ('technician', 'Technician'),
        ('business_manager', 'Business Manager'),
        ('business_user', 'Business User'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=USER_ROLES, default='business_user')
    is_active = models.BooleanField(default=True)
    has_documentation_access = models.BooleanField(default=False, help_text="Access to system documentation at /docs")  
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_profiles')
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"
    
    def can_manage_users(self):
        return self.role == 'application_admin'
    
    def can_view_system_notes(self):
        return self.role in ['application_admin', 'systems_manager']
    
    def can_create_records(self):
        return self.role in ['application_admin', 'systems_manager']
    
    def can_delete_records(self):
        return self.role in ['application_admin', 'systems_manager']
    
    def has_write_access(self):
        return self.role in ['application_admin', 'systems_manager', 'technician']
    
    def can_access_documentation(self):
        """Check if user can access system documentation"""
        # Application admins always have access (non-revokable)
        if self.role == 'application_admin':
            return True
        # Other users need explicit permission
        return self.has_documentation_access
    
    def save(self, *args, **kwargs):
        # Auto-grant documentation access for application admins (non-revokable)
        if self.role == 'application_admin':
            self.has_documentation_access = True
        # Auto-grant documentation access for systems managers (revokable)
        elif self.role == 'systems_manager' and not self.pk:  # Only on creation
            self.has_documentation_access = True
        super().save(*args, **kwargs)


class RecordPermission(AuditMixin, models.Model):
    """Explicit permissions for technicians and business users to access specific records"""
    PERMISSION_TYPES = [
        ('read', 'Read Only'),
        ('write', 'Read/Write'),
        ('full', 'Full Access'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='record_permissions')
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    permission_type = models.CharField(max_length=10, choices=PERMISSION_TYPES, default='read')
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['user', 'content_type', 'object_id']
        ordering = ['-granted_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.permission_type} access"


class CloudPlatform(AuditMixin, models.Model):
    """Cloud platforms that can host infrastructure (AWS, Azure, GCP, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)  # aws, azure, gcp, etc.
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    plugin_enabled = models.BooleanField(default=False)
    plugin_config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_cloud_platforms')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_cloud_platforms')
    system_manager_notes = models.TextField(blank=True, help_text="Only visible to Systems Managers and Application Admins")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ServerEnvironment(AuditMixin, models.Model):
    """Physical or virtual server environments"""
    ENVIRONMENT_TYPES = [
        ('physical', 'Physical Server'),
        ('virtual', 'Virtual Machine'),
        ('container', 'Container'),
        ('cloud', 'Cloud Instance'),
    ]
    
    name = models.CharField(max_length=200)
    hostname = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField()
    environment_type = models.CharField(max_length=20, choices=ENVIRONMENT_TYPES)
    operating_system = models.CharField(max_length=100)
    os_version = models.CharField(max_length=50)
    
    # Cloud-specific fields
    cloud_platform = models.ForeignKey(CloudPlatform, on_delete=models.CASCADE, null=True, blank=True)
    cloud_instance_id = models.CharField(max_length=100, blank=True)
    cloud_region = models.CharField(max_length=50, blank=True)
    
    # Physical/VM fields
    cpu_cores = models.PositiveIntegerField(null=True, blank=True)
    memory_gb = models.PositiveIntegerField(null=True, blank=True)
    storage_gb = models.PositiveIntegerField(null=True, blank=True)
    
    # Status and metadata
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    system_manager_notes = models.TextField(blank=True, help_text="Only visible to Systems Managers and Application Admins")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_servers')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_servers')

    class Meta:
        ordering = ['hostname']

    def __str__(self):
        return f"{self.hostname} ({self.ip_address})"


class Language(models.Model):
    """Programming languages and interpreters"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class DataStore(models.Model):
    """Database systems and data storage solutions"""
    DATASTORE_TYPES = [
        ('relational', 'Relational Database'),
        ('nosql', 'NoSQL Database'),
        ('cache', 'Cache Store'),
        ('search', 'Search Engine'),
        ('file', 'File Storage'),
        ('object', 'Object Storage'),
        ('queue', 'Message Queue'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    datastore_type = models.CharField(max_length=20, choices=DATASTORE_TYPES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_datastores')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_datastores')
    system_manager_notes = models.TextField(blank=True, help_text="Only visible to Systems Managers and Application Admins")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class LanguageInstallation(models.Model):
    """Language interpreters/runtimes installed on servers"""
    server = models.ForeignKey(ServerEnvironment, on_delete=models.CASCADE, related_name='language_installations')
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    version = models.CharField(max_length=50)
    installation_path = models.CharField(max_length=500, blank=True)
    is_default = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    system_manager_notes = models.TextField(blank=True, help_text="Only visible to Systems Managers and Application Admins")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_language_installations')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_language_installations')

    class Meta:
        unique_together = ['server', 'language', 'version']
        ordering = ['server', 'language', 'version']

    def __str__(self):
        return f"{self.language.name} {self.version} on {self.server.hostname}"


class DataStoreInstance(AuditMixin, models.Model):
    """Database instances running on servers"""
    server = models.ForeignKey(ServerEnvironment, on_delete=models.CASCADE, related_name='datastore_instances')
    datastore = models.ForeignKey(DataStore, on_delete=models.CASCADE)
    version = models.CharField(max_length=50)
    instance_name = models.CharField(max_length=200)
    port = models.PositiveIntegerField(null=True, blank=True)
    connection_string = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    system_manager_notes = models.TextField(blank=True, help_text="Only visible to Systems Managers and Application Admins")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_datastore_instances')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_datastore_instances')

    class Meta:
        unique_together = ['server', 'instance_name', 'port']
        ordering = ['server', 'datastore', 'instance_name']

    def __str__(self):
        return f"{self.datastore.name} ({self.instance_name}) on {self.server.hostname}"


class Application(AuditMixin, models.Model):
    """Enterprise applications tracked by the system"""
    LIFECYCLE_STAGES = [
        ('planning', 'Planning'),
        ('development', 'Development'),
        ('testing', 'Testing'),
        ('staging', 'Staging'),
        ('production', 'Production'),
        ('maintenance', 'Maintenance'),
        ('deprecated', 'Deprecated'),
        ('retired', 'Retired'),
    ]
    
    CRITICALITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Basic information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    business_purpose = models.TextField(help_text="What business function does this application serve?")
    
    # Lifecycle management
    lifecycle_stage = models.CharField(max_length=20, choices=LIFECYCLE_STAGES, default='development')
    criticality = models.CharField(max_length=20, choices=CRITICALITY_LEVELS, default='medium')
    
    # Ownership and contacts
    business_owner = models.CharField(max_length=200, help_text="Business unit or person responsible")
    technical_owner = models.CharField(max_length=200, help_text="Technical person or team responsible")
    
    # Hosting information
    primary_server = models.ForeignKey(ServerEnvironment, on_delete=models.PROTECT, related_name='primary_applications')
    additional_servers = models.ManyToManyField(ServerEnvironment, blank=True, related_name='secondary_applications')
    
    # Version and deployment info
    version = models.CharField(max_length=50, blank=True)
    deployment_path = models.CharField(max_length=500, blank=True)
    
    # Authentication
    uses_ldap = models.BooleanField(default=False, help_text="Does this application authenticate via LDAP/AD?")
    ldap_config = models.JSONField(default=dict, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    system_manager_notes = models.TextField(blank=True, help_text="Only visible to Systems Managers and Application Admins")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_applications')
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_applications')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.lifecycle_stage})"


class ApplicationLanguageDependency(models.Model):
    """Languages that an application depends on"""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='language_dependencies')
    language_installation = models.ForeignKey(LanguageInstallation, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False, help_text="Is this the primary language for the application?")
    notes = models.TextField(blank=True)
    system_manager_notes = models.TextField(blank=True, help_text="Only visible to Systems Managers and Application Admins")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_language_dependencies')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_language_dependencies')

    class Meta:
        unique_together = ['application', 'language_installation']
        ordering = ['application', '-is_primary', 'language_installation']

    def __str__(self):
        return f"{self.application.name} -> {self.language_installation}"


class ApplicationDataStoreDependency(models.Model):
    """Datastores that an application depends on"""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='datastore_dependencies')
    datastore_instance = models.ForeignKey(DataStoreInstance, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False, help_text="Is this the primary datastore for the application?")
    connection_type = models.CharField(max_length=50, blank=True, help_text="read-write, read-only, cache, etc.")
    notes = models.TextField(blank=True)
    system_manager_notes = models.TextField(blank=True, help_text="Only visible to Systems Managers and Application Admins")
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_datastore_dependencies')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_datastore_dependencies')

    class Meta:
        unique_together = ['application', 'datastore_instance']
        ordering = ['application', '-is_primary', 'datastore_instance']

    def __str__(self):
        return f"{self.application.name} -> {self.datastore_instance}"


class ApplicationLifecycleEvent(models.Model):
    """Track lifecycle changes for applications"""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='lifecycle_events')
    from_stage = models.CharField(max_length=20, choices=Application.LIFECYCLE_STAGES, null=True, blank=True)
    to_stage = models.CharField(max_length=20, choices=Application.LIFECYCLE_STAGES)
    event_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    system_manager_notes = models.TextField(blank=True, help_text="Only visible to Systems Managers and Application Admins")
    performed_by = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        ordering = ['application', '-event_date']

    def __str__(self):
        return f"{self.application.name}: {self.from_stage} -> {self.to_stage}"


class CloudPlugin(models.Model):
    """Registry of available cloud platform plugins"""
    name = models.CharField(max_length=100, unique=True)
    cloud_platform = models.ForeignKey(CloudPlatform, on_delete=models.CASCADE, related_name='plugins')
    plugin_module = models.CharField(max_length=200, help_text="Python module path for the plugin")
    version = models.CharField(max_length=50)
    description = models.TextField()
    is_enabled = models.BooleanField(default=False)
    configuration_schema = models.JSONField(default=dict, help_text="JSON schema for plugin configuration")
    system_manager_notes = models.TextField(blank=True, help_text="Only visible to Systems Managers and Application Admins")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_cloud_plugins')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_cloud_plugins')

    class Meta:
        ordering = ['cloud_platform', 'name']

    def __str__(self):
        return f"{self.cloud_platform.name}: {self.name}"
