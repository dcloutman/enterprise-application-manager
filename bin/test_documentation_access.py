#!/usr/bin/env python3

"""
Simple test script to verify documentation access system
"""

import os
import sys
import django
from django.conf import settings
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_tracker.settings')
django.setup()

from apps.inventory.models import UserProfile


def test_documentation_access():
    """Test documentation access functionality"""
    print("Testing Documentation Access System")
    print("=" * 50)
    
    # Create test users with different roles
    test_users = [
        ('admin', 'application_admin'),
        ('sysmanager', 'systems_manager'),
        ('technician', 'technician'),
        ('bizmanager', 'business_manager'),
        ('bizuser', 'business_user'),
    ]
    
    client = Client()
    
    for username, role in test_users:
        print(f"\nTesting user: {username} (role: {role})")
        
        # Create or get user
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'first_name': username.title(),
                'last_name': 'User'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
        
        # Create or update profile
        profile, prof_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': role}
        )
        
        if not prof_created:
            profile.role = role
            profile.save()
        
        # Test access permissions
        print(f"  - Can access documentation: {profile.can_access_documentation()}")
        print(f"  - Has documentation access flag: {profile.has_documentation_access}")
        print(f"  - Role: {profile.get_role_display()}")
        
        # Test web access
        client.login(username=username, password='testpass123')
        response = client.get('/docs/')
        
        if profile.can_access_documentation():
            if response.status_code == 302:  # Redirect to actual docs
                print(f"  - Web access: ALLOWED (redirected to docs)")
            else:
                print(f"  - Web access: ERROR (status {response.status_code})")
        else:
            if response.status_code == 200 and 'access denied' in response.content.decode().lower():
                print(f"  - Web access: CORRECTLY DENIED")
            else:
                print(f"  - Web access: ERROR (should be denied, got {response.status_code})")
    
    print("\n" + "=" * 50)
    print("Documentation access test completed")


def test_access_status_api():
    """Test the documentation access status API"""
    print("\nTesting Documentation Access Status API")
    print("=" * 50)
    
    client = Client()
    
    # Test with admin user
    user = User.objects.get(username='admin')
    client.login(username='admin', password='testpass123')
    
    response = client.get('/docs/status/')
    print("API Response for admin user:")
    print(response.content.decode())


if __name__ == '__main__':
    try:
        test_documentation_access()
        test_access_status_api()
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
