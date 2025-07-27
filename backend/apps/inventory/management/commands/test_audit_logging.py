from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.inventory.models import UserProfile, CloudPlatform, Application
from apps.inventory.audit import audit_logger


class Command(BaseCommand):
    help = 'Test the audit logging system by creating, updating, and deleting records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            default='admin',
            help='Username to use for audit logging test (default: admin)',
        )

    def handle(self, *args, **options):
        username = options['user']
        
        # Get or create test user
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"Using existing user: {username}")
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='testpass123'
            )
            self.stdout.write(f"Created test user: {username}")
        
        # Set the user for audit logging
        audit_logger.set_current_user(user)
        
        self.stdout.write("Testing audit logging system...")
        
        # Test 1: Create a CloudPlatform
        self.stdout.write("\n1. Testing CREATE operation...")
        platform = CloudPlatform.objects.create(
            name='Test AWS',
            code='test-aws',
            description='Test AWS platform for audit logging',
            is_active=True
        )
        self.stdout.write(f"Created CloudPlatform: {platform}")
        
        # Test 2: Update the CloudPlatform
        self.stdout.write("\n2. Testing UPDATE operation...")
        platform.description = 'Updated description for audit test'
        platform.plugin_enabled = True
        platform.save()
        self.stdout.write(f"Updated CloudPlatform: {platform}")
        
        # Test 3: Create an Application
        self.stdout.write("\n3. Testing CREATE with foreign key...")
        app = Application.objects.create(
            name='Test Application',
            description='Test app for audit logging',
            business_owner='Test Owner',
            technical_contact='tech@example.com',
            lifecycle_stage='development',
            criticality_level='medium'
        )
        self.stdout.write(f"Created Application: {app}")
        
        # Test 4: Update Application with multiple field changes
        self.stdout.write("\n4. Testing UPDATE with multiple changes...")
        app.description = 'Updated test application description'
        app.lifecycle_stage = 'testing'
        app.criticality_level = 'high'
        app.is_active = False
        app.save()
        self.stdout.write(f"Updated Application: {app}")
        
        # Test 5: Create UserProfile (if not exists)
        self.stdout.write("\n5. Testing UserProfile operations...")
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': 'application_admin',
                'department': 'IT',
                'phone': '555-1234',
                'has_documentation_access': True
            }
        )
        if created:
            self.stdout.write(f"Created UserProfile: {profile}")
        else:
            # Update existing profile
            profile.department = 'Engineering'
            profile.phone = '555-5678'
            profile.save()
            self.stdout.write(f"Updated UserProfile: {profile}")
        
        # Test 6: Delete records
        self.stdout.write("\n6. Testing DELETE operations...")
        app.delete()
        self.stdout.write(f"Deleted Application: {app.name}")
        
        platform.delete()
        self.stdout.write(f"Deleted CloudPlatform: {platform.name}")
        
        # Clean up
        audit_logger.set_current_user(None)
        
        # Show where logs are written
        from django.conf import settings
        log_file = f"{getattr(settings, 'AUDIT_LOG_DIR', '/var/log/app-tracker')}/audit.log"
        
        self.stdout.write(f"\nAudit logging test completed!")
        self.stdout.write(f"Check audit logs at: {log_file}")
        self.stdout.write("\nSample log format:")
        self.stdout.write("[YYYY-MM-DD HH:MM:SS] ACTION ModelName#ID by USERNAME: Object Description | Changes: field1: old -> new | JSON: {...}")
        
        # Manual log entry to show direct logging capability
        audit_logger.log_change(
            action='TEST',
            model_name='System',
            object_id='test',
            object_str='Audit logging test completed',
            user=user,
            additional_info={'test_run': True, 'timestamp': 'manual'}
        )
