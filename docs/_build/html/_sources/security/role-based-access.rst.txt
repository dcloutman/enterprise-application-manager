Role-Based Access Control
=========================

The Enterprise Application Tracker implements a comprehensive role-based access control (RBAC) system designed for government and enterprise security requirements.

Security Architecture
---------------------

**Defense in Depth**

The RBAC system implements multiple layers of security:

1. **Authentication Layer**: User identity verification
2. **Authorization Layer**: Role-based permission checking
3. **Data Layer**: Record-level access control
4. **Audit Layer**: Complete action logging
5. **Network Layer**: Transport security and access controls

**Zero Trust Principles**

* **Never Trust, Always Verify**: Every request is authenticated and authorized
* **Least Privilege Access**: Users receive minimum necessary permissions
* **Assume Breach**: System designed to limit damage from compromised accounts
* **Verify Explicitly**: All access decisions based on multiple data points

Role Security Model
-------------------

**Hierarchical Permissions**

.. code-block::

    ┌─────────────────────────────────────────────────────┐
    │  Application Admin (Level 5)                       │
    │  ├── Full system access                            │
    │  ├── User management                               │
    │  ├── Security configuration                        │
    │  └── Audit access                                  │
    └─────────────────────────────────────────────────────┘
             ┌──────────────────────────────────────────┐
             │  Systems Manager (Level 4)              │
             │  ├── Technical data access              │
             │  ├── System notes visibility           │
             │  ├── Infrastructure management         │
             │  └── No user management                 │
             └──────────────────────────────────────────┘
                      ┌─────────────────────────────────┐
                      │  Technician (Level 3)          │
                      │  ├── Limited write access      │
                      │  ├── Assigned record editing   │
                      │  ├── No system notes          │
                      │  └── No record creation       │
                      └─────────────────────────────────┘
                               ┌────────────────────────┐
                               │  Business Manager (2) │
                               │  ├── Read-only access │
                               │  ├── Business reports │
                               │  ├── No technical data│
                               │  └── No system notes  │
                               └────────────────────────┘
                                        ┌──────────────┐
                                        │ Business (1) │
                                        │ ├── Basic    │
                                        │ ├── Public   │
                                        │ ├── Info     │
                                        │ └── Only     │
                                        └──────────────┘

**Permission Inheritance**

Higher-level roles inherit all permissions from lower levels, plus additional capabilities:

.. code-block:: python

    # Permission checking logic
    def has_permission(user_role, required_permission):
        role_hierarchy = {
            'business_user': 1,
            'business_manager': 2,
            'technician': 3,
            'systems_manager': 4,
            'application_admin': 5
        }
        
        permission_levels = {
            'view_public': 1,
            'view_business': 2,
            'edit_assigned': 3,
            'view_system_notes': 4,
            'manage_users': 5
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = permission_levels.get(required_permission, 0)
        
        return user_level >= required_level

Access Control Implementation
-----------------------------

**Database-Level Security**

Row-level security ensures users only see authorized data:

.. code-block:: sql

    -- Example: Server access control
    CREATE POLICY server_access_policy ON servers
        FOR ALL TO authenticated_users
        USING (
            -- Application Admins see all
            current_user_role() = 'application_admin' OR
            -- Systems Managers see all
            current_user_role() = 'systems_manager' OR
            -- Technicians see assigned servers
            (current_user_role() = 'technician' AND 
             EXISTS (SELECT 1 FROM server_assignments 
                    WHERE server_id = servers.id 
                    AND user_id = current_user_id())) OR
            -- Business users see non-sensitive servers
            (current_user_role() IN ('business_manager', 'business_user') AND
             servers.is_public = true)
        );

**API-Level Security**

All API endpoints implement permission checking:

.. code-block:: python

    from rest_framework.permissions import BasePermission

    class CanViewSystemNotes(BasePermission):
        def has_permission(self, request, view):
            if not request.user.is_authenticated:
                return False
            
            try:
                profile = request.user.profile
                return profile.can_view_system_notes()
            except UserProfile.DoesNotExist:
                return False

    class ServerViewSet(ModelViewSet):
        permission_classes = [IsAuthenticated, CanViewSystemNotes]
        
        def get_queryset(self):
            user = self.request.user
            if user.profile.role in ['application_admin', 'systems_manager']:
                return Server.objects.all()
            elif user.profile.role == 'technician':
                return Server.objects.filter(
                    assignments__user=user,
                    assignments__is_active=True
                )
            else:
                return Server.objects.filter(is_public=True)

**UI-Level Security**

Frontend components respect role permissions:

.. code-block:: javascript

    // Svelte component with role-based rendering
    <script lang="ts">
        import { user } from '$lib/stores/auth';
        
        $: canManageUsers = $user?.profile?.permissions?.can_manage_users;
        $: canViewSystemNotes = $user?.profile?.permissions?.can_view_system_notes;
    </script>

    {#if canManageUsers}
        <button on:click={openUserManagement}>Manage Users</button>
    {/if}

    {#if canViewSystemNotes}
        <div class="system-notes">
            <h3>System Manager Notes</h3>
            <p>{server.system_manager_notes}</p>
        </div>
    {/if}

Data Classification
-------------------

**Information Sensitivity Levels**

.. list-table::
   :widths: 20 30 25 25
   :header-rows: 1

   * - **Level**
     - **Description**
     - **Access Requirements**
     - **Examples**
   * - Public
     - Non-sensitive business information
     - All authenticated users
     - Application names, general descriptions
   * - Internal
     - Internal business information
     - Business Manager+ roles
     - Cost centers, business owners
   * - Confidential
     - Technical system information
     - Technician+ roles
     - Server configurations, versions
   * - Restricted
     - Sensitive technical details
     - Systems Manager+ roles
     - Security configurations, credentials
   * - Top Secret
     - Critical security information
     - Application Admin only
     - Encryption keys, admin passwords

**System Notes Security**

System Manager Notes contain sensitive technical information:

.. code-block:: python

    class ServerSerializer(ModelSerializer):
        system_manager_notes = SerializerMethodField()
        
        def get_system_manager_notes(self, obj):
            user = self.context['request'].user
            if hasattr(user, 'profile') and user.profile.can_view_system_notes():
                return obj.system_manager_notes
            return None  # Hidden from unauthorized users

Multi-Factor Authentication
---------------------------

**MFA Requirements**

* **Application Admins**: MFA mandatory
* **Systems Managers**: MFA required for production systems
* **Other Roles**: MFA recommended, configurable by policy

**Supported MFA Methods**

1. **TOTP (Time-based One-Time Password)**
   - Google Authenticator
   - Microsoft Authenticator
   - Authy

2. **Hardware Tokens**
   - YubiKey
   - RSA SecurID
   - FIDO2/WebAuthn

3. **SMS/Email** (not recommended for high-security environments)

**MFA Configuration**

.. code-block:: python

    # Django settings for MFA
    INSTALLED_APPS = [
        'django_otp',
        'django_otp.plugins.otp_totp',
        'django_otp.plugins.otp_static',
    ]

    MIDDLEWARE = [
        'django_otp.middleware.OTPMiddleware',
    ]

    # Custom MFA enforcement
    class MFARequiredMixin:
        def dispatch(self, request, *args, **kwargs):
            if not request.user.is_verified():
                if request.user.profile.role == 'application_admin':
                    return redirect('two_factor:setup')
            return super().dispatch(request, *args, **kwargs)

Session Security
----------------

**Session Configuration**

.. code-block:: python

    # Secure session settings
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
    SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
    SESSION_COOKIE_AGE = 3600  # 1 hour timeout
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True
    SESSION_SAVE_EVERY_REQUEST = True  # Extend on activity

**Session Management**

.. code-block:: python

    def login_view(request):
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                # Check for concurrent sessions
                if user.profile.max_concurrent_sessions:
                    active_sessions = Session.objects.filter(
                        user=user,
                        expire_date__gt=timezone.now()
                    ).count()
                    
                    if active_sessions >= user.profile.max_concurrent_sessions:
                        return JsonResponse({
                            'error': 'Maximum concurrent sessions exceeded'
                        }, status=403)
                
                login(request, user)
                
                # Log successful login
                audit_log.info(f"User {username} logged in from {request.META['REMOTE_ADDR']}")
                
                return redirect('dashboard')

Password Security
-----------------

**Password Requirements**

* **Minimum Length**: 12 characters
* **Complexity**: Must include uppercase, lowercase, numbers, symbols
* **History**: Cannot reuse last 12 passwords
* **Expiration**: 90 days for privileged accounts, 180 days for others
* **Lockout**: 5 failed attempts triggers 15-minute lockout

**Password Policy Implementation**

.. code-block:: python

    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError

    class EnterprisePasswordValidator:
        def validate(self, password, user=None):
            if len(password) < 12:
                raise ValidationError("Password must be at least 12 characters.")
            
            if not re.search(r'[A-Z]', password):
                raise ValidationError("Password must contain uppercase letters.")
            
            if not re.search(r'[a-z]', password):
                raise ValidationError("Password must contain lowercase letters.")
            
            if not re.search(r'\d', password):
                raise ValidationError("Password must contain numbers.")
            
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValidationError("Password must contain special characters.")
            
            # Check password history
            if user and hasattr(user, 'password_history'):
                for old_password in user.password_history.all()[:12]:
                    if check_password(password, old_password.password_hash):
                        raise ValidationError("Cannot reuse recent passwords.")

**Account Lockout Protection**

.. code-block:: python

    from django.contrib.auth.signals import user_login_failed
    from django.dispatch import receiver
    from django.core.cache import cache

    @receiver(user_login_failed)
    def handle_login_failed(sender, credentials, request, **kwargs):
        username = credentials.get('username')
        if username:
            cache_key = f"failed_login_{username}"
            failed_attempts = cache.get(cache_key, 0) + 1
            
            if failed_attempts >= 5:
                # Lock account for 15 minutes
                cache.set(f"locked_{username}", True, 900)
                audit_log.warning(f"Account {username} locked due to failed login attempts")
            
            cache.set(cache_key, failed_attempts, 900)

Permission Auditing
-------------------

**Real-time Permission Monitoring**

.. code-block:: python

    class PermissionAuditMiddleware:
        def __init__(self, get_response):
            self.get_response = get_response

        def __call__(self, request):
            # Log permission checks
            if request.user.is_authenticated:
                audit_log.info(f"User {request.user.username} accessing {request.path}")
                
                # Check for privilege escalation attempts
                if hasattr(request, 'permission_denied'):
                    audit_log.warning(f"Permission denied for {request.user.username} on {request.path}")
            
            response = self.get_response(request)
            return response

**Regular Access Reviews**

.. code-block:: python

    # Management command for access review
    class Command(BaseCommand):
        def handle(self, *args, **options):
            # Generate access review report
            high_privilege_users = UserProfile.objects.filter(
                role__in=['application_admin', 'systems_manager']
            )
            
            for profile in high_privilege_users:
                last_login = profile.user.last_login
                if last_login and (timezone.now() - last_login).days > 30:
                    self.stdout.write(f"REVIEW: {profile.user.username} - no login for 30+ days")
                
                # Check for orphaned permissions
                permissions = RecordPermission.objects.filter(user=profile.user)
                for perm in permissions:
                    if perm.expires_at and perm.expires_at < timezone.now():
                        self.stdout.write(f"CLEANUP: Expired permission for {profile.user.username}")

Security Monitoring
-------------------

**Automated Threat Detection**

.. code-block:: python

    class SecurityMonitoringService:
        @staticmethod
        def detect_anomalous_access(user, resource):
            # Check for unusual access patterns
            recent_access = AccessLog.objects.filter(
                user=user,
                timestamp__gte=timezone.now() - timedelta(hours=24)
            )
            
            if recent_access.count() > 1000:  # Unusually high activity
                alert_security_team(f"High activity detected for user {user.username}")
            
            # Check for access outside normal hours
            if timezone.now().hour < 6 or timezone.now().hour > 22:
                if user.profile.role in ['application_admin', 'systems_manager']:
                    alert_security_team(f"After-hours admin access: {user.username}")
            
            # Check for geographic anomalies (if IP geolocation available)
            current_ip = get_client_ip(request)
            usual_locations = get_user_usual_locations(user)
            if not is_location_familiar(current_ip, usual_locations):
                require_additional_verification(user)

**Security Compliance Reporting**

.. code-block:: python

    def generate_security_compliance_report():
        report = {
            'user_access_summary': {},
            'privileged_account_review': {},
            'security_violations': {},
            'audit_trail_integrity': {}
        }
        
        # User access patterns
        for profile in UserProfile.objects.all():
            report['user_access_summary'][profile.user.username] = {
                'role': profile.role,
                'last_login': profile.user.last_login,
                'failed_logins': get_failed_login_count(profile.user),
                'permissions': list(profile.user.record_permissions.values_list('permission_type', flat=True))
            }
        
        return report
