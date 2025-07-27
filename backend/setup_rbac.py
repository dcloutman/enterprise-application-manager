#!/usr/bin/env python3.12
"""
Simple script to test the role-based access control system
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_tracker.settings')
django.setup()

from django.contrib.auth.models import User
from apps.inventory.models import UserProfile


def create_test_users():
    """Create test users with different roles"""
    print("🚀 Setting up role-based access control system...")
    
    # Create admin user profile for existing admin user
    try:
        admin_user = User.objects.get(username='admin')
        admin_profile, created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'role': 'application_admin',
                'department': 'IT Administration',
                'phone': '555-0001'
            }
        )
        print(f"✅ Admin profile: {admin_profile} (created: {created})")
    except User.DoesNotExist:
        print("❌ Admin user not found")
        return False

    # Create test users with different roles
    users_data = [
        {
            'username': 'sysmanager',
            'email': 'sysmanager@example.com',
            'password': 'manager123',
            'first_name': 'System',
            'last_name': 'Manager',
            'role': 'systems_manager',
            'department': 'IT Operations',
            'phone': '555-0002'
        },
        {
            'username': 'technician',
            'email': 'tech@example.com',
            'password': 'tech123',
            'first_name': 'Tech',
            'last_name': 'User',
            'role': 'technician',
            'department': 'IT Support',
            'phone': '555-0003'
        },
        {
            'username': 'bizmanager',
            'email': 'bizmanager@example.com',
            'password': 'biz123',
            'first_name': 'Business',
            'last_name': 'Manager',
            'role': 'business_manager',
            'department': 'Operations',
            'phone': '555-0004'
        },
        {
            'username': 'bizuser',
            'email': 'bizuser@example.com',
            'password': 'user123',
            'first_name': 'Business',
            'last_name': 'User',
            'role': 'business_user',
            'department': 'Operations',
            'phone': '555-0005'
        }
    ]
    
    for user_data in users_data:
        try:
            # Try to get existing user or create new one
            user, user_created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name']
                }
            )
            
            if user_created:
                user.set_password(user_data['password'])
                user.save()
                print(f"✅ Created user: {user.username}")
            else:
                print(f"🔄 User exists: {user.username}")
            
            # Create or update profile
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': user_data['role'],
                    'department': user_data['department'],
                    'phone': user_data['phone']
                }
            )
            
            if profile_created:
                print(f"✅ Created profile: {profile}")
            else:
                print(f"🔄 Profile exists: {profile}")
                
        except Exception as e:
            print(f"❌ Error creating user {user_data['username']}: {e}")
    
    return True


def test_permissions():
    """Test role-based permissions for different users"""
    print("\n🔐 Testing role-based permissions...")
    
    profiles = UserProfile.objects.all()
    for profile in profiles:
        print(f"\n👤 {profile.user.username} ({profile.get_role_display()}):")
        print(f"   🔧 Can manage users: {profile.can_manage_users()}")
        print(f"   👁️  Can view system notes: {profile.can_view_system_notes()}")
        print(f"   ➕ Can create records: {profile.can_create_records()}")
        print(f"   🗑️  Can delete records: {profile.can_delete_records()}")
        print(f"   ✏️  Has write access: {profile.has_write_access()}")


def display_summary():
    """Display a summary of the user management system"""
    print("\n📊 User Management System Summary:")
    print("=" * 50)
    
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    total_profiles = UserProfile.objects.count()
    
    print(f"Total Users: {total_users}")
    print(f"Active Users: {active_users}")
    print(f"User Profiles: {total_profiles}")
    
    print("\nUsers by Role:")
    role_counts = {}
    for profile in UserProfile.objects.all():
        role_display = profile.get_role_display()
        role_counts[role_display] = role_counts.get(role_display, 0) + 1
    
    for role, count in role_counts.items():
        print(f"  • {role}: {count}")
    
    print("\n🎯 Role-Based Access Control System is ready!")
    print("\nNext steps:")
    print("1. Access admin panel at http://localhost/admin/ (admin/admin123)")
    print("2. Test API endpoints for user management")
    print("3. Implement frontend user management interface")
    print("4. Hide admin panel from end users in production")


if __name__ == "__main__":
    try:
        if create_test_users():
            test_permissions()
            display_summary()
        else:
            print("❌ Failed to set up test users")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
