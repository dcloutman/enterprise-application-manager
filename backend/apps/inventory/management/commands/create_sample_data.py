from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.inventory.models import (
    CloudPlatform, ServerEnvironment, Language, DataStore,
    LanguageInstallation, DataStoreInstance, Application,
    ApplicationLanguageDependency, ApplicationDataStoreDependency
)


class Command(BaseCommand):
    help = 'Create sample data for the IT asset management system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create cloud platforms
        aws, _ = CloudPlatform.objects.get_or_create(
            code='aws',
            defaults={
                'name': 'Amazon Web Services',
                'description': 'Amazon Web Services cloud platform',
                'plugin_enabled': True,
                'plugin_config': {
                    'region': 'us-east-1',
                    'access_key_id': 'SAMPLE_KEY',
                    'secret_access_key': 'SAMPLE_SECRET',
                    'api_endpoint': 'https://ec2.amazonaws.com'
                }
            }
        )

        azure, _ = CloudPlatform.objects.get_or_create(
            code='azure',
            defaults={
                'name': 'Microsoft Azure',
                'description': 'Microsoft Azure cloud platform',
                'plugin_enabled': True,
                'plugin_config': {
                    'api_endpoint': 'https://management.azure.com'
                }
            }
        )

        # Create server environments
        prod_web, _ = ServerEnvironment.objects.get_or_create(
            hostname='web-prod-01',
            defaults={
                'name': 'Production Web Server 1',
                'ip_address': '10.0.1.10',
                'environment_type': 'production',
                'operating_system': 'Oracle Linux',
                'os_version': '8.4',
                'cloud_platform': aws,
                'cloud_instance_id': 'i-1234567890abcdef0',
                'cpu_cores': 4,
                'memory_gb': 16,
                'storage_gb': 100
            }
        )

        dev_web, _ = ServerEnvironment.objects.get_or_create(
            hostname='web-dev-01',
            defaults={
                'name': 'Development Web Server',
                'ip_address': '10.0.2.10',
                'environment_type': 'development',
                'operating_system': 'Oracle Linux',
                'os_version': '8.4',
                'cpu_cores': 2,
                'memory_gb': 8,
                'storage_gb': 50
            }
        )

        db_server, _ = ServerEnvironment.objects.get_or_create(
            hostname='db-prod-01',
            defaults={
                'name': 'Production Database Server',
                'ip_address': '10.0.1.20',
                'environment_type': 'production',
                'operating_system': 'Oracle Linux',
                'os_version': '8.4',
                'cloud_platform': aws,
                'cloud_instance_id': 'i-abcdef1234567890',
                'cpu_cores': 8,
                'memory_gb': 32,
                'storage_gb': 500
            }
        )

        # Create languages
        python, _ = Language.objects.get_or_create(name='Python')
        java, _ = Language.objects.get_or_create(name='Java')
        nodejs, _ = Language.objects.get_or_create(name='Node.js')
        php, _ = Language.objects.get_or_create(name='PHP')

        # Create datastores
        mysql, _ = DataStore.objects.get_or_create(
            name='MySQL',
            defaults={'datastore_type': 'relational'}
        )
        postgres, _ = DataStore.objects.get_or_create(
            name='PostgreSQL',
            defaults={'datastore_type': 'relational'}
        )
        redis, _ = DataStore.objects.get_or_create(
            name='Redis',
            defaults={'datastore_type': 'cache'}
        )

        # Create language installations
        python_prod, _ = LanguageInstallation.objects.get_or_create(
            language=python,
            version='3.12.0',
            server=prod_web,
            defaults={'is_default': True, 'installation_path': '/usr/bin/python3.12'}
        )

        python_dev, _ = LanguageInstallation.objects.get_or_create(
            language=python,
            version='3.12.0',
            server=dev_web,
            defaults={'is_default': True, 'installation_path': '/usr/bin/python3.12'}
        )

        java_prod, _ = LanguageInstallation.objects.get_or_create(
            language=java,
            version='17.0.8',
            server=prod_web,
            defaults={'is_default': True, 'installation_path': '/usr/lib/jvm/java-17-openjdk'}
        )

        nodejs_dev, _ = LanguageInstallation.objects.get_or_create(
            language=nodejs,
            version='22.5.1',
            server=dev_web,
            defaults={'is_default': True, 'installation_path': '/usr/local/bin/node'}
        )

        # Create datastore instances
        mysql_prod, _ = DataStoreInstance.objects.get_or_create(
            datastore=mysql,
            instance_name='main_db',
            server=db_server,
            defaults={
                'version': '8.4.0',
                'port': 3306,
                'connection_string': 'mysql://user:pass@db-prod-01:3306/app_tracker'
            }
        )

        redis_prod, _ = DataStoreInstance.objects.get_or_create(
            datastore=redis,
            instance_name='cache_cluster',
            server=prod_web,
            defaults={
                'version': '7.0.12',
                'port': 6379,
                'connection_string': 'redis://prod-web-01:6379/0'
            }
        )

        # Get a user for application ownership
        try:
            admin_user = User.objects.get(username='claudevandam')
        except User.DoesNotExist:
            admin_user = User.objects.create_user(
                username='sample_user',
                email='sample@example.org',
                password='samplepass'
            )

        # Create sample applications
        web_portal, _ = Application.objects.get_or_create(
            name='Employee Web Portal',
            defaults={
                'description': 'Internal web portal for employee services',
                'business_purpose': 'Provides employees access to HR services, payroll, and benefits',
                'version': '2.1.4',
                'lifecycle_stage': 'production',
                'criticality': 'high',
                'business_owner': 'HR Director',
                'technical_owner': 'IT Development Team',
                'primary_server': prod_web,
                'deployment_path': '/opt/webportal',
                'uses_ldap': True,
                'ldap_config': {
                    'server': 'ldap.company.gov',
                    'base_dn': 'dc=company,dc=gov',
                    'bind_dn': 'cn=webportal,ou=services,dc=company,dc=gov'
                },
                'created_by': admin_user,
                'updated_by': admin_user
            }
        )

        api_service, _ = Application.objects.get_or_create(
            name='Data Analytics API',
            defaults={
                'description': 'REST API for enterprise data analytics',
                'business_purpose': 'Provides data analytics capabilities for enterprise reporting',
                'version': '1.3.2',
                'lifecycle_stage': 'production',
                'criticality': 'medium',
                'business_owner': 'Analytics Director',
                'technical_owner': 'Data Team Lead',
                'primary_server': prod_web,
                'deployment_path': '/opt/analytics-api',
                'uses_ldap': False,
                'created_by': admin_user,
                'updated_by': admin_user
            }
        )

        dev_app, _ = Application.objects.get_or_create(
            name='Testing Framework',
            defaults={
                'description': 'Automated testing framework for enterprise applications',
                'business_purpose': 'Quality assurance and automated testing',
                'version': '0.8.1',
                'lifecycle_stage': 'development',
                'criticality': 'low',
                'business_owner': 'QA Manager',
                'technical_owner': 'QA Team Lead',
                'primary_server': dev_web,
                'deployment_path': '/opt/testing-framework',
                'uses_ldap': True,
                'created_by': admin_user,
                'updated_by': admin_user
            }
        )

        # Create application dependencies
        # Web portal uses Python and MySQL
        ApplicationLanguageDependency.objects.get_or_create(
            application=web_portal,
            language_installation=python_prod,
            defaults={'is_primary': True, 'notes': 'Django web framework'}
        )

        ApplicationDataStoreDependency.objects.get_or_create(
            application=web_portal,
            datastore_instance=mysql_prod,
            defaults={
                'is_primary': True,
                'connection_type': 'read_write',
                'notes': 'Main application database'
            }
        )

        ApplicationDataStoreDependency.objects.get_or_create(
            application=web_portal,
            datastore_instance=redis_prod,
            defaults={
                'is_primary': False,
                'connection_type': 'read_write',
                'notes': 'Session cache and temporary data'
            }
        )

        # API service uses Python and MySQL
        ApplicationLanguageDependency.objects.get_or_create(
            application=api_service,
            language_installation=python_prod,
            defaults={'is_primary': True, 'notes': 'FastAPI framework'}
        )

        ApplicationDataStoreDependency.objects.get_or_create(
            application=api_service,
            datastore_instance=mysql_prod,
            defaults={
                'is_primary': True,
                'connection_type': 'read_only',
                'notes': 'Analytics data source'
            }
        )

        # Development app uses Node.js
        ApplicationLanguageDependency.objects.get_or_create(
            application=dev_app,
            language_installation=nodejs_dev,
            defaults={'is_primary': True, 'notes': 'Jest testing framework'}
        )

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )

        # Display summary
        self.stdout.write('\nSample Data Summary:')
        self.stdout.write(f'Cloud Platforms: {CloudPlatform.objects.count()}')
        self.stdout.write(f'Server Environments: {ServerEnvironment.objects.count()}')
        self.stdout.write(f'Languages: {Language.objects.count()}')
        self.stdout.write(f'Data Stores: {DataStore.objects.count()}')
        self.stdout.write(f'Language Installations: {LanguageInstallation.objects.count()}')
        self.stdout.write(f'DataStore Instances: {DataStoreInstance.objects.count()}')
        self.stdout.write(f'Applications: {Application.objects.count()}')
        self.stdout.write(f'Language Dependencies: {ApplicationLanguageDependency.objects.count()}')
        self.stdout.write(f'DataStore Dependencies: {ApplicationDataStoreDependency.objects.count()}')
