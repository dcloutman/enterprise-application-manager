Data Protection and Privacy
===========================

The Enterprise Application Tracker implements comprehensive data protection measures to ensure compliance with government regulations and enterprise privacy requirements.

Data Classification Framework
-----------------------------

**Classification Levels**

.. list-table::
   :widths: 15 25 30 30
   :header-rows: 1

   * - **Level**
     - **Description**
     - **Protection Requirements**
     - **Examples**
   * - **Public**
     - Information approved for public release
     - Standard access controls
     - Application descriptions, general documentation
   * - **Internal**
     - Internal business information
     - Authentication required
     - Cost centers, business processes
   * - **Confidential**
     - Sensitive business/technical data
     - Role-based access + encryption
     - Server configurations, performance data
   * - **Restricted**
     - Highly sensitive information
     - Multi-factor auth + audit logging
     - Security settings, admin credentials
   * - **Top Secret**
     - Critical security information
     - Highest privileges + special handling
     - Encryption keys, security vulnerabilities

**Automatic Classification**

.. code-block:: python

    class DataClassificationService:
        @staticmethod
        def classify_field(model_class, field_name, value):
            # Automatic classification based on field patterns
            classification_rules = {
                'password': 'TOP_SECRET',
                'secret': 'TOP_SECRET',
                'key': 'TOP_SECRET',
                'token': 'RESTRICTED',
                'admin': 'RESTRICTED',
                'system_manager_notes': 'RESTRICTED',
                'cost_center': 'INTERNAL',
                'business_owner': 'INTERNAL',
                'description': 'PUBLIC'
            }
            
            for pattern, level in classification_rules.items():
                if pattern in field_name.lower():
                    return level
            
            # Content-based classification
            if re.search(r'\b(password|secret|private)\b', str(value).lower()):
                return 'TOP_SECRET'
            elif re.search(r'\b(admin|root|privileged)\b', str(value).lower()):
                return 'RESTRICTED'
            
            return 'INTERNAL'  # Default classification

Encryption at Rest
------------------

**Database Encryption**

.. code-block:: python

    # Field-level encryption for sensitive data
    from cryptography.fernet import Fernet
    from django.conf import settings

    class EncryptedField(models.TextField):
        def __init__(self, *args, **kwargs):
            self.fernet = Fernet(settings.FIELD_ENCRYPTION_KEY)
            super().__init__(*args, **kwargs)
        
        def from_db_value(self, value, expression, connection):
            if value is None:
                return value
            try:
                return self.fernet.decrypt(value.encode()).decode()
            except:
                return value  # Fallback for unencrypted legacy data
        
        def to_python(self, value):
            return value
        
        def get_prep_value(self, value):
            if value is None:
                return value
            return self.fernet.encrypt(value.encode()).decode()

    # Model with encrypted fields
    class Server(models.Model):
        name = models.CharField(max_length=100)
        system_manager_notes = EncryptedField(blank=True)
        admin_password = EncryptedField(blank=True)
        
        class Meta:
            db_table = 'servers'

**File System Encryption**

.. code-block:: yaml

    # Docker volume encryption
    version: '3.8'
    services:
      mysql:
        volumes:
          - type: volume
            source: mysql_data_encrypted
            target: /var/lib/mysql
            volume:
              driver_opts:
                type: "encrypted"
                device: "/dev/mapper/mysql-data"

    volumes:
      mysql_data_encrypted:
        driver: local
        driver_opts:
          type: luks
          device: /dev/sdb1

**Backup Encryption**

.. code-block:: bash

    #!/bin/bash
    # Encrypted backup script
    
    # Database backup with encryption
    mysqldump --single-transaction app_tracker | \
    gpg --symmetric --cipher-algo AES256 --compress-algo 2 --s2k-mode 3 \
        --s2k-digest-algo SHA512 --s2k-count 65011712 --quiet --no-greeting \
        > backup_$(date +%Y%m%d_%H%M%S).sql.gpg
    
    # File backup with tar and gpg
    tar czf - /app/media /app/logs | \
    gpg --symmetric --cipher-algo AES256 --compress-algo 2 --s2k-mode 3 \
        --s2k-digest-algo SHA512 --s2k-count 65011712 --quiet --no-greeting \
        > files_backup_$(date +%Y%m%d_%H%M%S).tar.gz.gpg

Encryption in Transit
---------------------

**HTTPS Configuration**

.. code-block:: nginx

    # Nginx SSL configuration
    server {
        listen 443 ssl http2;
        server_name app-tracker.example.com;
        
        # SSL certificates
        ssl_certificate /etc/ssl/certs/app-tracker.crt;
        ssl_certificate_key /etc/ssl/private/app-tracker.key;
        
        # SSL security settings
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        
        # HSTS
        add_header Strict-Transport-Security "max-age=63072000" always;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'";
        
        location / {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

**Database Connection Security**

.. code-block:: python

    # Django database settings with SSL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'app_tracker',
            'USER': 'app_user',
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': 'mysql',
            'PORT': '3306',
            'OPTIONS': {
                'ssl': {
                    'ca': '/etc/ssl/certs/ca-cert.pem',
                    'cert': '/etc/ssl/certs/client-cert.pem',
                    'key': '/etc/ssl/private/client-key.pem',
                },
                'sql_mode': 'STRICT_TRANS_TABLES',
                'charset': 'utf8mb4',
                'use_unicode': True,
            },
        }
    }

**API Security**

.. code-block:: python

    # Secure API communication
    class SecureAPIMiddleware:
        def __init__(self, get_response):
            self.get_response = get_response

        def __call__(self, request):
            # Enforce HTTPS
            if not request.is_secure() and not settings.DEBUG:
                return HttpResponsePermanentRedirect(
                    'https://' + request.get_host() + request.get_full_path()
                )
            
            # Validate Content-Type for POST/PUT requests
            if request.method in ['POST', 'PUT', 'PATCH']:
                if not request.content_type.startswith('application/json'):
                    return HttpResponseBadRequest('Invalid Content-Type')
            
            response = self.get_response(request)
            
            # Security headers
            response['X-Frame-Options'] = 'DENY'
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            return response

Data Retention Policies
-----------------------

**Retention Schedules**

.. list-table::
   :widths: 30 20 25 25
   :header-rows: 1

   * - **Data Type**
     - **Retention Period**
     - **Archive Period**
     - **Disposal Method**
   * - User Activity Logs
     - 2 years
     - 5 years
     - Secure deletion
   * - System Configuration
     - 5 years
     - 10 years
     - Encrypted archive
   * - Business Data
     - 7 years
     - Indefinite
     - Migration to archive
   * - Security Logs
     - 5 years
     - 10 years
     - Encrypted archive
   * - Personal Data
     - As required by law
     - N/A
     - Right to erasure

**Automated Retention Management**

.. code-block:: python

    from django.core.management.base import BaseCommand
    from datetime import datetime, timedelta

    class Command(BaseCommand):
        help = 'Apply data retention policies'

        def handle(self, *args, **options):
            # Activity logs retention (2 years)
            cutoff_date = datetime.now() - timedelta(days=730)
            old_logs = ActivityLog.objects.filter(timestamp__lt=cutoff_date)
            
            self.stdout.write(f'Archiving {old_logs.count()} activity logs')
            for log in old_logs:
                # Archive to long-term storage
                archive_log(log)
                log.delete()
            
            # Personal data cleanup (GDPR compliance)
            inactive_users = User.objects.filter(
                last_login__lt=datetime.now() - timedelta(days=1095),  # 3 years
                is_active=False
            )
            
            for user in inactive_users:
                if user.profile.role == 'business_user':
                    # Anonymize personal data
                    user.first_name = f'Deleted User {user.id}'
                    user.last_name = ''
                    user.email = f'deleted_{user.id}@example.com'
                    user.save()
                    
                    self.stdout.write(f'Anonymized user {user.username}')

**Data Archival Process**

.. code-block:: python

    def archive_data(model_class, archive_date):
        """Archive old data to long-term storage"""
        
        # Export to encrypted JSON
        old_records = model_class.objects.filter(
            modified_date__lt=archive_date
        )
        
        archive_data = []
        for record in old_records:
            # Serialize with encryption for sensitive fields
            serialized = model_to_dict(record)
            
            # Encrypt sensitive fields
            for field_name, value in serialized.items():
                if is_sensitive_field(model_class, field_name):
                    serialized[field_name] = encrypt_field_value(value)
            
            archive_data.append(serialized)
        
        # Store in encrypted archive
        archive_file = f'archive_{model_class.__name__}_{archive_date.strftime("%Y%m%d")}.json.gpg'
        encrypted_data = encrypt_json(archive_data)
        
        with open(f'/archives/{archive_file}', 'wb') as f:
            f.write(encrypted_data)
        
        # Verify archive integrity
        if verify_archive_integrity(archive_file):
            # Remove from active database
            old_records.delete()
            logger.info(f'Archived {len(archive_data)} {model_class.__name__} records')
        else:
            logger.error(f'Archive verification failed for {model_class.__name__}')

Privacy Controls
----------------

**Data Minimization**

.. code-block:: python

    class DataMinimizationMixin:
        """Ensure only necessary data is collected and stored"""
        
        def clean(self):
            super().clean()
            
            # Remove unnecessary whitespace and normalize data
            for field in self._meta.fields:
                if isinstance(field, (models.CharField, models.TextField)):
                    value = getattr(self, field.name)
                    if value:
                        setattr(self, field.name, value.strip())
            
            # Validate data necessity
            self.validate_data_necessity()
        
        def validate_data_necessity(self):
            """Override in subclasses to validate data collection"""
            pass

**Consent Management**

.. code-block:: python

    class ConsentRecord(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        consent_type = models.CharField(max_length=50, choices=[
            ('data_processing', 'Data Processing'),
            ('analytics', 'Analytics'),
            ('marketing', 'Marketing Communications'),
        ])
        granted = models.BooleanField()
        granted_date = models.DateTimeField()
        withdrawn_date = models.DateTimeField(null=True, blank=True)
        consent_version = models.CharField(max_length=10)
        
        class Meta:
            unique_together = ['user', 'consent_type']

    def check_consent(user, consent_type):
        """Check if user has granted specific consent"""
        try:
            consent = ConsentRecord.objects.get(
                user=user,
                consent_type=consent_type
            )
            return consent.granted and consent.withdrawn_date is None
        except ConsentRecord.DoesNotExist:
            return False

**Right to Erasure (GDPR Article 17)**

.. code-block:: python

    class DataErasureService:
        @staticmethod
        def process_erasure_request(user, reason):
            """Process user's right to erasure request"""
            
            # Log the request
            ErasureRequest.objects.create(
                user=user,
                reason=reason,
                requested_date=timezone.now(),
                status='pending'
            )
            
            # Check if erasure is legally required
            if DataErasureService.can_erase_user_data(user):
                return DataErasureService.erase_user_data(user)
            else:
                return {
                    'success': False,
                    'reason': 'Legal obligations prevent data erasure'
                }
        
        @staticmethod
        def erase_user_data(user):
            """Securely erase user's personal data"""
            
            # Anonymize instead of delete to preserve system integrity
            user.first_name = f'Erased User'
            user.last_name = ''
            user.email = f'erased_{uuid.uuid4()}@example.com'
            user.username = f'erased_{user.id}'
            user.is_active = False
            user.save()
            
            # Remove profile data
            if hasattr(user, 'profile'):
                profile = user.profile
                profile.phone_number = ''
                profile.department = ''
                profile.save()
            
            # Remove from activity logs (where legally permissible)
            ActivityLog.objects.filter(user=user).update(
                user=None,
                user_identifier=f'erased_user_{user.id}'
            )
            
            # Secure deletion of cached data
            cache.delete_many([
                f'user_profile_{user.id}',
                f'user_permissions_{user.id}',
                f'user_activity_{user.id}'
            ])
            
            return {'success': True, 'message': 'User data erased successfully'}

**Data Portability (GDPR Article 20)**

.. code-block:: python

    class DataPortabilityService:
        @staticmethod
        def export_user_data(user):
            """Export user's data in portable format"""
            
            export_data = {
                'personal_information': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'date_joined': user.date_joined.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                },
                'profile_data': {},
                'activity_logs': [],
                'permissions': [],
                'created_records': []
            }
            
            # Profile data
            if hasattr(user, 'profile'):
                export_data['profile_data'] = {
                    'role': user.profile.role,
                    'department': user.profile.department,
                    'phone_number': user.profile.phone_number,
                    'created_date': user.profile.created_date.isoformat(),
                }
            
            # Activity logs (last 2 years)
            cutoff_date = timezone.now() - timedelta(days=730)
            activity_logs = ActivityLog.objects.filter(
                user=user,
                timestamp__gte=cutoff_date
            )
            
            for log in activity_logs:
                export_data['activity_logs'].append({
                    'action': log.action,
                    'timestamp': log.timestamp.isoformat(),
                    'ip_address': log.ip_address,
                    'details': log.details
                })
            
            # User permissions
            permissions = RecordPermission.objects.filter(user=user)
            for perm in permissions:
                export_data['permissions'].append({
                    'permission_type': perm.permission_type,
                    'granted_date': perm.granted_date.isoformat(),
                    'expires_at': perm.expires_at.isoformat() if perm.expires_at else None,
                })
            
            # Records created by user
            for model_class in [Application, Server, DataStore]:
                records = model_class.objects.filter(created_by=user)
                for record in records:
                    export_data['created_records'].append({
                        'type': model_class.__name__,
                        'id': record.id,
                        'name': getattr(record, 'name', str(record)),
                        'created_date': record.created_date.isoformat(),
                    })
            
            return export_data

Data Loss Prevention
--------------------

**Automated DLP Scanning**

.. code-block:: python

    class DLPScanner:
        @staticmethod
        def scan_for_sensitive_data(text):
            """Scan text for sensitive information patterns"""
            
            patterns = {
                'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
                'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                'password': r'(password|pwd|pass)\s*[:=]\s*\S+',
            }
            
            findings = []
            for pattern_name, pattern in patterns.items():
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    findings.append({
                        'type': pattern_name,
                        'match': match.group(),
                        'position': match.span(),
                        'severity': 'HIGH' if pattern_name in ['ssn', 'credit_card'] else 'MEDIUM'
                    })
            
            return findings
        
        @staticmethod
        def prevent_data_exfiltration(request, response_data):
            """Prevent sensitive data from leaving the system"""
            
            if isinstance(response_data, dict):
                response_str = json.dumps(response_data)
            else:
                response_str = str(response_data)
            
            findings = DLPScanner.scan_for_sensitive_data(response_str)
            
            if findings:
                # Log potential data leak
                logger.warning(f'Potential data leak prevented for user {request.user.username}')
                
                # Remove sensitive data
                for finding in findings:
                    if finding['severity'] == 'HIGH':
                        response_str = response_str.replace(
                            finding['match'],
                            '[REDACTED]'
                        )
                
                # Return sanitized data
                try:
                    return json.loads(response_str)
                except:
                    return response_str
            
            return response_data

**File Upload Security**

.. code-block:: python

    class SecureFileUploadHandler:
        ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.csv']
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        
        @staticmethod
        def validate_file(uploaded_file):
            """Validate uploaded file for security"""
            
            # Check file size
            if uploaded_file.size > SecureFileUploadHandler.MAX_FILE_SIZE:
                raise ValidationError('File too large')
            
            # Check file extension
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            if file_ext not in SecureFileUploadHandler.ALLOWED_EXTENSIONS:
                raise ValidationError('File type not allowed')
            
            # Scan for malware (integrate with antivirus)
            if not SecureFileUploadHandler.scan_for_malware(uploaded_file):
                raise ValidationError('File failed security scan')
            
            # Check for sensitive data
            content = uploaded_file.read()
            uploaded_file.seek(0)  # Reset file pointer
            
            if isinstance(content, bytes):
                try:
                    content = content.decode('utf-8')
                except UnicodeDecodeError:
                    # Binary file, skip content scan
                    return True
            
            findings = DLPScanner.scan_for_sensitive_data(content)
            high_risk_findings = [f for f in findings if f['severity'] == 'HIGH']
            
            if high_risk_findings:
                raise ValidationError('File contains sensitive information')
            
            return True
