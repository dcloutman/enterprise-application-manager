"""
Test suite for inventory models
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .models import (
    UserProfile, RecordPermission, CloudPlatform, ServerEnvironment,
    Language, DataStore, LanguageInstallation, DataStoreInstance,
    Application, ApplicationLanguageDependency, ApplicationDataStoreDependency,
    ApplicationLifecycleEvent, CloudPlugin
)


class UserProfileModelTest(TestCase):
    """Test UserProfile model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123'
        )
        self.regular_user = User.objects.create_user(
            username='testuser',
            email='user@test.com',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        """Test UserProfile model creation and validation"""
        profile = UserProfile.objects.create(
            user=self.admin_user,
            role='systems_manager',
            department='Engineering',
            phone='555-1234'
        )
        
        self.assertEqual(profile.role, 'systems_manager')
        self.assertEqual(profile.department, 'Engineering')
        self.assertTrue(profile.has_documentation_access)  # Auto-granted for sys managers
        self.assertTrue(profile.can_view_system_notes())
        self.assertTrue(profile.can_create_records())
    
    def test_application_admin_permissions(self):
        """Test application admin permissions"""
        admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            role='application_admin',
            department='IT'
        )
        
        self.assertTrue(admin_profile.can_manage_users())
        self.assertTrue(admin_profile.can_view_system_notes())
        self.assertTrue(admin_profile.can_create_records())
        self.assertTrue(admin_profile.can_delete_records())
        self.assertTrue(admin_profile.can_access_documentation())
        self.assertTrue(admin_profile.has_documentation_access)  # Auto-granted, non-revokable
    
    def test_business_user_permissions(self):
        """Test business user permissions"""
        user_profile = UserProfile.objects.create(
            user=self.regular_user,
            role='business_user',
            department='Sales'
        )
        
        self.assertFalse(user_profile.can_manage_users())
        self.assertFalse(user_profile.can_view_system_notes())
        self.assertFalse(user_profile.can_create_records())
        self.assertFalse(user_profile.can_delete_records())
        self.assertFalse(user_profile.can_access_documentation())
        self.assertFalse(user_profile.has_documentation_access)  # No auto-access
    
    def test_documentation_access_auto_assignment(self):
        """Test automatic documentation access assignment"""
        # Application admin - auto-granted, non-revokable
        admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            role='application_admin'
        )
        self.assertTrue(admin_profile.has_documentation_access)
        
        # Try to revoke access - should be re-granted on save
        admin_profile.has_documentation_access = False
        admin_profile.save()
        admin_profile.refresh_from_db()
        self.assertTrue(admin_profile.has_documentation_access)  # Should be auto-restored
        
        # Systems manager - auto-granted on creation but revokable
        sys_user = User.objects.create_user('sysmanager', 'sys@test.com', 'pass')
        sys_profile = UserProfile.objects.create(
            user=sys_user,
            role='systems_manager'
        )
        self.assertTrue(sys_profile.has_documentation_access)
        
        # Should be revokable for systems managers
        sys_profile.has_documentation_access = False
        sys_profile.save()
        sys_profile.refresh_from_db()
        self.assertFalse(sys_profile.has_documentation_access)
    
    def test_user_profile_string_representation(self):
        """Test UserProfile string representation"""
        profile = UserProfile.objects.create(
            user=self.admin_user,
            role='technician'
        )
        
        expected = f"{self.admin_user.get_full_name() or self.admin_user.username} (Technician)"
        self.assertEqual(str(profile), expected)


class CloudPlatformModelTest(TestCase):
    """Test CloudPlatform model functionality"""
    
    def test_cloud_platform_creation(self):
        """Test CloudPlatform model creation"""
        platform = CloudPlatform.objects.create(
            name='Test AWS',
            code='test-aws',
            description='Test AWS platform',
            is_active=True,
            plugin_enabled=False
        )
        
        self.assertEqual(platform.name, 'Test AWS')
        self.assertEqual(platform.code, 'test-aws')
        self.assertTrue(platform.is_active)
        self.assertFalse(platform.plugin_enabled)
        self.assertEqual(str(platform), 'Test AWS')
    
    def test_cloud_platform_unique_constraints(self):
        """Test unique constraints on CloudPlatform"""
        CloudPlatform.objects.create(
            name='AWS',
            code='aws',
            description='Amazon Web Services'
        )
        
        # Test unique name constraint
        with self.assertRaises(IntegrityError):
            CloudPlatform.objects.create(
                name='AWS',  # Duplicate name
                code='aws2',
                description='Another AWS'
            )
        
        # Test unique code constraint
        with self.assertRaises(IntegrityError):
            CloudPlatform.objects.create(
                name='AWS 2',
                code='aws',  # Duplicate code
                description='Another AWS'
            )


class ServerEnvironmentModelTest(TestCase):
    """Test ServerEnvironment model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.cloud_platform = CloudPlatform.objects.create(
            name='AWS',
            code='aws',
            description='Amazon Web Services'
        )
    
    def test_server_environment_creation(self):
        """Test ServerEnvironment model creation"""
        server = ServerEnvironment.objects.create(
            name='Test Server',
            hostname='test-server-01',
            ip_address='10.0.1.100',
            operating_system='Ubuntu 22.04',
            os_version='22.04.3',
            environment_type='development',
            cloud_platform=self.cloud_platform,
            cpu_cores=4,
            memory_gb=16,
            storage_gb=500
        )
        
        self.assertEqual(server.hostname, 'test-server-01')
        self.assertEqual(server.ip_address, '10.0.1.100')
        self.assertEqual(server.cloud_platform, self.cloud_platform)
        self.assertEqual(server.cpu_cores, 4)
        self.assertEqual(str(server), 'test-server-01 (10.0.1.100)')
    
    def test_server_environment_unique_hostname(self):
        """Test unique hostname constraint"""
        ServerEnvironment.objects.create(
            name='Server 1',
            hostname='unique-server',
            ip_address='10.0.1.101',
            operating_system='Ubuntu 22.04',
            os_version='22.04.3',
            environment_type='production'
        )
        
        # Test unique hostname constraint
        with self.assertRaises(IntegrityError):
            ServerEnvironment.objects.create(
                name='Server 2',
                hostname='unique-server',  # Duplicate hostname
                ip_address='10.0.1.102',
                operating_system='Ubuntu 22.04',
                os_version='22.04.3',
                environment_type='development'
            )


class ApplicationModelTest(TestCase):
    """Test Application model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        self.server = ServerEnvironment.objects.create(
            name='App Server',
            hostname='app-server-01',
            ip_address='10.0.1.102',
            operating_system='Ubuntu 22.04',
            os_version='22.04.3',
            environment_type='production'
        )
    
    def test_application_creation(self):
        """Test Application model creation"""
        app = Application.objects.create(
            name='Test Application',
            description='A test application',
            business_purpose='Testing purposes',
            business_owner='Test Owner',
            technical_owner='Tech Team',
            primary_server=self.server,
            lifecycle_stage='development',
            criticality='medium',
            created_by=self.user,
            updated_by=self.user
        )
        
        self.assertEqual(app.name, 'Test Application')
        self.assertEqual(app.lifecycle_stage, 'development')
        self.assertEqual(app.criticality, 'medium')
        self.assertTrue(app.is_active)  # Default True
        self.assertEqual(app.primary_server, self.server)
        self.assertIsNotNone(app.id)  # UUID should be generated
        
        # Test string representation
        self.assertEqual(str(app), 'Test Application (development)')
    
    def test_application_lifecycle_stages(self):
        """Test application lifecycle stage transitions"""
        app = Application.objects.create(
            name='Lifecycle Test App',
            description='Testing lifecycle stages',
            business_purpose='Testing',
            business_owner='Owner',
            technical_owner='Tech',
            primary_server=self.server,
            lifecycle_stage='planning',
            created_by=self.user,
            updated_by=self.user
        )
        
        # Test valid lifecycle stages
        valid_stages = ['planning', 'development', 'testing', 'staging', 'production', 'maintenance', 'deprecated', 'retired']
        
        for stage in valid_stages:
            app.lifecycle_stage = stage
            app.save()
            app.refresh_from_db()
            self.assertEqual(app.lifecycle_stage, stage)


class LanguageAndDataStoreTest(TestCase):
    """Test Language and DataStore models"""
    
    def test_language_creation(self):
        """Test Language model creation"""
        language = Language.objects.create(
            name='Python',
            description='Python programming language',
            is_active=True
        )
        
        self.assertEqual(language.name, 'Python')
        self.assertTrue(language.is_active)
        self.assertEqual(str(language), 'Python')
    
    def test_datastore_creation(self):
        """Test DataStore model creation"""
        datastore = DataStore.objects.create(
            name='PostgreSQL',
            datastore_type='relational',
            description='PostgreSQL database'
        )
        
        self.assertEqual(datastore.name, 'PostgreSQL')
        self.assertEqual(datastore.datastore_type, 'relational')
        self.assertEqual(str(datastore), 'PostgreSQL')


class InstallationAndInstanceTest(TestCase):
    """Test LanguageInstallation and DataStoreInstance models"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        
        self.server = ServerEnvironment.objects.create(
            name='Test Server',
            hostname='test-server',
            ip_address='10.0.1.103',
            operating_system='Ubuntu 22.04',
            os_version='22.04.3',
            environment_type='development'
        )
        
        self.language = Language.objects.create(
            name='Python',
            is_active=True
        )
        
        self.datastore = DataStore.objects.create(
            name='MySQL',
            datastore_type='relational'
        )
    
    def test_language_installation(self):
        """Test LanguageInstallation model"""
        installation = LanguageInstallation.objects.create(
            server=self.server,
            language=self.language,
            version='3.11',
            installation_path='/usr/bin/python3.11',
            is_default=True,
            created_by=self.user,
            updated_by=self.user
        )
        
        self.assertEqual(installation.server, self.server)
        self.assertEqual(installation.language, self.language)
        self.assertEqual(installation.version, '3.11')
        self.assertTrue(installation.is_default)
        
        expected_str = f"{self.language.name} {installation.version} on {self.server.hostname}"
        self.assertEqual(str(installation), expected_str)
    
    def test_datastore_instance(self):
        """Test DataStoreInstance model"""
        instance = DataStoreInstance.objects.create(
            server=self.server,
            datastore=self.datastore,
            version='8.0',
            instance_name='test-db',
            port=3306,
            is_active=True,
            created_by=self.user,
            updated_by=self.user
        )
        
        self.assertEqual(instance.server, self.server)
        self.assertEqual(instance.datastore, self.datastore)
        self.assertEqual(instance.version, '8.0')
        self.assertEqual(instance.port, 3306)
        
        expected_str = f"{self.datastore.name} ({instance.instance_name}) on {self.server.hostname}"
        self.assertEqual(str(instance), expected_str)


class DependencyRelationshipTest(TestCase):
    """Test application dependency relationships"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        
        self.server = ServerEnvironment.objects.create(
            name='App Server',
            hostname='app-server',
            ip_address='10.0.1.104',
            operating_system='Ubuntu 22.04',
            os_version='22.04.3',
            environment_type='production'
        )
        
        self.language = Language.objects.create(name='Python', is_active=True)
        self.lang_install = LanguageInstallation.objects.create(
            language=self.language,
            server=self.server,
            version='3.11',
            installation_path='/usr/bin/python3.11',
            created_by=self.user,
            updated_by=self.user
        )
        
        self.datastore = DataStore.objects.create(
            name='PostgreSQL',
            datastore_type='relational'
        )
        self.ds_instance = DataStoreInstance.objects.create(
            server=self.server,
            datastore=self.datastore,
            version='14',
            instance_name='app-db',
            port=5432,
            created_by=self.user,
            updated_by=self.user
        )
        
        self.app = Application.objects.create(
            name='Web App',
            description='Test web application',
            business_purpose='Web services',
            business_owner='Owner',
            technical_owner='Tech Team',
            primary_server=self.server,
            created_by=self.user,
            updated_by=self.user
        )
    
    def test_application_language_dependency(self):
        """Test ApplicationLanguageDependency model"""
        lang_dep = ApplicationLanguageDependency.objects.create(
            application=self.app,
            language_installation=self.lang_install,
            is_primary=True,
            created_by=self.user,
            updated_by=self.user
        )
        
        self.assertEqual(lang_dep.application, self.app)
        self.assertEqual(lang_dep.language_installation, self.lang_install)
        self.assertTrue(lang_dep.is_primary)
        
        expected_str = f"{self.app.name} -> {self.lang_install}"
        self.assertEqual(str(lang_dep), expected_str)
    
    def test_application_datastore_dependency(self):
        """Test ApplicationDataStoreDependency model"""
        db_dep = ApplicationDataStoreDependency.objects.create(
            application=self.app,
            datastore_instance=self.ds_instance,
            is_primary=True,
            connection_type='read-write',
            created_by=self.user,
            updated_by=self.user
        )
        
        self.assertEqual(db_dep.application, self.app)
        self.assertEqual(db_dep.datastore_instance, self.ds_instance)
        self.assertTrue(db_dep.is_primary)
        self.assertEqual(db_dep.connection_type, 'read-write')
        
        expected_str = f"{self.app.name} -> {self.ds_instance}"
        self.assertEqual(str(db_dep), expected_str)


class RecordPermissionTest(TestCase):
    """Test RecordPermission model"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user('admin', 'admin@test.com', 'pass')
        self.regular_user = User.objects.create_user('user', 'user@test.com', 'pass')
        
        self.server = ServerEnvironment.objects.create(
            name='Test Server',
            hostname='perm-test-server',
            ip_address='10.0.1.105',
            operating_system='Ubuntu 22.04',
            os_version='22.04.3',
            environment_type='development'
        )
        
        self.app = Application.objects.create(
            name='Permission Test App',
            description='App for testing permissions',
            business_purpose='Testing',
            business_owner='Owner',
            technical_owner='Tech',
            primary_server=self.server,
            created_by=self.admin_user,
            updated_by=self.admin_user
        )
    
    def test_record_permission_creation(self):
        """Test RecordPermission model creation"""
        from django.contrib.contenttypes.models import ContentType
        
        app_content_type = ContentType.objects.get_for_model(Application)
        
        permission = RecordPermission.objects.create(
            user=self.regular_user,
            content_type=app_content_type,
            object_id=str(self.app.id),  # UUID as string
            permission_type='read',
            granted_by=self.admin_user,
            notes='Test permission grant'
        )
        
        self.assertEqual(permission.user, self.regular_user)
        self.assertEqual(permission.permission_type, 'read')
        self.assertEqual(permission.granted_by, self.admin_user)
        self.assertEqual(str(permission), f"{self.regular_user.username} - read access")
