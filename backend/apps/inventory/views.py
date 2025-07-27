from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Prefetch
from django.contrib.auth.models import User

from .models import (
    CloudPlatform, ServerEnvironment, Language, DataStore,
    LanguageInstallation, DataStoreInstance, Application,
    ApplicationLanguageDependency, ApplicationDataStoreDependency,
    ApplicationLifecycleEvent, CloudPlugin
)
from .serializers import (
    CloudPlatformSerializer, ServerEnvironmentSerializer, LanguageSerializer,
    DataStoreSerializer, LanguageInstallationSerializer, DataStoreInstanceSerializer,
    ApplicationSerializer, ApplicationLanguageDependencySerializer,
    ApplicationDataStoreDependencySerializer, ApplicationLifecycleEventSerializer,
    CloudPluginSerializer, ApplicationDetailSerializer, ServerEnvironmentDetailSerializer
)


class CloudPlatformViewSet(viewsets.ModelViewSet):
    queryset = CloudPlatform.objects.all()
    serializer_class = CloudPlatformSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'plugin_enabled']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def servers(self, request, pk=None):
        """Get all servers for this cloud platform"""
        cloud_platform = self.get_object()
        servers = cloud_platform.servers.all()
        serializer = ServerEnvironmentSerializer(servers, many=True)
        return Response(serializer.data)


class ServerEnvironmentViewSet(viewsets.ModelViewSet):
    queryset = ServerEnvironment.objects.select_related('cloud_platform').prefetch_related(
        'primary_applications', 'additional_applications', 'language_installations__language',
        'datastore_instances__datastore'
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['environment_type', 'operating_system', 'is_active', 'cloud_platform']
    search_fields = ['name', 'hostname', 'ip_address']
    ordering_fields = ['hostname', 'created_at', 'environment_type']
    ordering = ['hostname']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ServerEnvironmentDetailSerializer
        return ServerEnvironmentSerializer

    @action(detail=True, methods=['get'])
    def applications(self, request, pk=None):
        """Get all applications running on this server"""
        server = self.get_object()
        primary_apps = server.primary_applications.all()
        additional_apps = server.additional_applications.all()
        
        primary_data = ApplicationSerializer(primary_apps, many=True).data
        additional_data = ApplicationSerializer(additional_apps, many=True).data
        
        return Response({
            'primary_applications': primary_data,
            'additional_applications': additional_data,
            'total_count': len(primary_data) + len(additional_data)
        })

    @action(detail=True, methods=['get'])
    def resources(self, request, pk=None):
        """Get language installations and datastore instances on this server"""
        server = self.get_object()
        languages = LanguageInstallationSerializer(server.language_installations.all(), many=True).data
        datastores = DataStoreInstanceSerializer(server.datastore_instances.all(), many=True).data
        
        return Response({
            'language_installations': languages,
            'datastore_instances': datastores
        })


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def installations(self, request, pk=None):
        """Get all installations of this language"""
        language = self.get_object()
        installations = language.installations.select_related('server').all()
        serializer = LanguageInstallationSerializer(installations, many=True)
        return Response(serializer.data)


class DataStoreViewSet(viewsets.ModelViewSet):
    queryset = DataStore.objects.all()
    serializer_class = DataStoreSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['datastore_type', 'is_active']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def instances(self, request, pk=None):
        """Get all instances of this datastore"""
        datastore = self.get_object()
        instances = datastore.datastoreinstance_set.select_related('server').all()
        serializer = DataStoreInstanceSerializer(instances, many=True)
        return Response(serializer.data)


class LanguageInstallationViewSet(viewsets.ModelViewSet):
    queryset = LanguageInstallation.objects.select_related('language', 'server').all()
    serializer_class = LanguageInstallationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['language', 'server', 'is_default', 'server__environment_type']
    search_fields = ['language__name', 'version', 'server__hostname']
    ordering_fields = ['language__name', 'version', 'server__hostname', 'created_at']
    ordering = ['language__name', 'server__hostname']


class DataStoreInstanceViewSet(viewsets.ModelViewSet):
    queryset = DataStoreInstance.objects.select_related('datastore', 'server').all()
    serializer_class = DataStoreInstanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['datastore', 'server', 'is_active', 'server__environment_type']
    search_fields = ['datastore__name', 'instance_name', 'server__hostname']
    ordering_fields = ['datastore__name', 'instance_name', 'server__hostname', 'created_at']
    ordering = ['datastore__name', 'server__hostname']


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.select_related(
        'primary_server', 'created_by', 'updated_by'
    ).prefetch_related(
        'additional_servers',
        'language_dependencies__language_installation__language',
        'language_dependencies__language_installation__server',
        'datastore_dependencies__datastore_instance__datastore',
        'datastore_dependencies__datastore_instance__server',
        'lifecycle_events__performed_by'
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'lifecycle_stage', 'criticality', 'is_active', 'uses_ldap',
        'primary_server', 'primary_server__environment_type'
    ]
    search_fields = ['name', 'description', 'business_owner', 'technical_owner']
    ordering_fields = ['name', 'lifecycle_stage', 'criticality', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ApplicationDetailSerializer
        return ApplicationSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        # Track lifecycle changes
        if 'lifecycle_stage' in serializer.validated_data:
            original = self.get_object()
            new_stage = serializer.validated_data['lifecycle_stage']
            if original.lifecycle_stage != new_stage:
                ApplicationLifecycleEvent.objects.create(
                    application=original,
                    from_stage=original.lifecycle_stage,
                    to_stage=new_stage,
                    performed_by=self.request.user
                )
        
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def change_lifecycle_stage(self, request, pk=None):
        """Explicitly change lifecycle stage with tracking"""
        application = self.get_object()
        new_stage = request.data.get('lifecycle_stage')
        
        if not new_stage:
            return Response(
                {'error': 'lifecycle_stage is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_stage not in dict(Application.LIFECYCLE_STAGES):
            return Response(
                {'error': 'Invalid lifecycle stage'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_stage = application.lifecycle_stage
        application.lifecycle_stage = new_stage
        application.updated_by = request.user
        application.save()
        
        # Create lifecycle event
        ApplicationLifecycleEvent.objects.create(
            application=application,
            from_stage=old_stage,
            to_stage=new_stage,
            performed_by=request.user
        )
        
        return Response({
            'message': f'Lifecycle stage changed from {old_stage} to {new_stage}',
            'application': ApplicationSerializer(application).data
        })

    @action(detail=True, methods=['get'])
    def dependencies(self, request, pk=None):
        """Get all dependencies for this application"""
        application = self.get_object()
        language_deps = ApplicationLanguageDependencySerializer(
            application.language_dependencies.all(), many=True
        ).data
        datastore_deps = ApplicationDataStoreDependencySerializer(
            application.datastore_dependencies.all(), many=True
        ).data
        
        return Response({
            'language_dependencies': language_deps,
            'datastore_dependencies': datastore_deps
        })

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics"""
        total_apps = Application.objects.count()
        apps_by_stage = Application.objects.values('lifecycle_stage').annotate(
            count=Count('id')
        ).order_by('lifecycle_stage')
        apps_by_criticality = Application.objects.values('criticality').annotate(
            count=Count('id')
        ).order_by('criticality')
        
        return Response({
            'total_applications': total_apps,
            'by_lifecycle_stage': list(apps_by_stage),
            'by_criticality': list(apps_by_criticality),
            'active_applications': Application.objects.filter(is_active=True).count(),
            'inactive_applications': Application.objects.filter(is_active=False).count()
        })


class ApplicationLanguageDependencyViewSet(viewsets.ModelViewSet):
    queryset = ApplicationLanguageDependency.objects.select_related(
        'application', 'language_installation__language', 'language_installation__server'
    ).all()
    serializer_class = ApplicationLanguageDependencySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['application', 'language_installation__language', 'is_primary']
    search_fields = ['application__name', 'language_installation__language__name']
    ordering_fields = ['application__name', 'language_installation__language__name', 'created_at']
    ordering = ['application__name']


class ApplicationDataStoreDependencyViewSet(viewsets.ModelViewSet):
    queryset = ApplicationDataStoreDependency.objects.select_related(
        'application', 'datastore_instance__datastore', 'datastore_instance__server'
    ).all()
    serializer_class = ApplicationDataStoreDependencySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['application', 'datastore_instance__datastore', 'is_primary', 'connection_type']
    search_fields = ['application__name', 'datastore_instance__datastore__name']
    ordering_fields = ['application__name', 'datastore_instance__datastore__name', 'created_at']
    ordering = ['application__name']


class ApplicationLifecycleEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ApplicationLifecycleEvent.objects.select_related(
        'application', 'performed_by'
    ).order_by('-event_date')
    serializer_class = ApplicationLifecycleEventSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['application', 'from_stage', 'to_stage', 'performed_by']
    ordering_fields = ['event_date']
    ordering = ['-event_date']


class CloudPluginViewSet(viewsets.ModelViewSet):
    queryset = CloudPlugin.objects.select_related('cloud_platform').all()
    serializer_class = CloudPluginSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['cloud_platform', 'is_enabled']
    search_fields = ['name', 'plugin_module']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
