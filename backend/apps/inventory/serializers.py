from rest_framework import serializers
from .models import (
    CloudPlatform, ServerEnvironment, Language, DataStore,
    LanguageInstallation, DataStoreInstance, Application,
    ApplicationLanguageDependency, ApplicationDataStoreDependency,
    ApplicationLifecycleEvent, CloudPlugin
)


class CloudPlatformSerializer(serializers.ModelSerializer):
    server_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CloudPlatform
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_server_count(self, obj):
        return obj.servers.count()


class ServerEnvironmentSerializer(serializers.ModelSerializer):
    cloud_platform_name = serializers.CharField(source='cloud_platform.name', read_only=True)
    application_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ServerEnvironment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_application_count(self, obj):
        return obj.primary_applications.count() + obj.additional_applications.count()


class LanguageSerializer(serializers.ModelSerializer):
    installation_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Language
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_installation_count(self, obj):
        return obj.installations.count()


class DataStoreSerializer(serializers.ModelSerializer):
    instance_count = serializers.SerializerMethodField()
    
    class Meta:
        model = DataStore
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_instance_count(self, obj):
        return obj.datastoreinstance_set.count()


class LanguageInstallationSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(source='language.name', read_only=True)
    server_hostname = serializers.CharField(source='server.hostname', read_only=True)
    
    class Meta:
        model = LanguageInstallation
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class DataStoreInstanceSerializer(serializers.ModelSerializer):
    datastore_name = serializers.CharField(source='datastore.name', read_only=True)
    datastore_type = serializers.CharField(source='datastore.datastore_type', read_only=True)
    server_hostname = serializers.CharField(source='server.hostname', read_only=True)
    
    class Meta:
        model = DataStoreInstance
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ApplicationLanguageDependencySerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(source='language_installation.language.name', read_only=True)
    language_version = serializers.CharField(source='language_installation.version', read_only=True)
    server_hostname = serializers.CharField(source='language_installation.server.hostname', read_only=True)
    
    class Meta:
        model = ApplicationLanguageDependency
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ApplicationDataStoreDependencySerializer(serializers.ModelSerializer):
    datastore_name = serializers.CharField(source='datastore_instance.datastore.name', read_only=True)
    datastore_type = serializers.CharField(source='datastore_instance.datastore.datastore_type', read_only=True)
    server_hostname = serializers.CharField(source='datastore_instance.server.hostname', read_only=True)
    
    class Meta:
        model = ApplicationDataStoreDependency
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ApplicationLifecycleEventSerializer(serializers.ModelSerializer):
    performed_by_username = serializers.CharField(source='performed_by.username', read_only=True)
    
    class Meta:
        model = ApplicationLifecycleEvent
        fields = '__all__'
        read_only_fields = ('event_date',)


class ApplicationSerializer(serializers.ModelSerializer):
    primary_server_hostname = serializers.CharField(source='primary_server.hostname', read_only=True)
    additional_servers_hostnames = serializers.SerializerMethodField()
    language_dependencies = ApplicationLanguageDependencySerializer(many=True, read_only=True)
    datastore_dependencies = ApplicationDataStoreDependencySerializer(many=True, read_only=True)
    lifecycle_events = ApplicationLifecycleEventSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_additional_servers_hostnames(self, obj):
        return [server.hostname for server in obj.additional_servers.all()]


class CloudPluginSerializer(serializers.ModelSerializer):
    cloud_platform_name = serializers.CharField(source='cloud_platform.name', read_only=True)
    
    class Meta:
        model = CloudPlugin
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


# Detailed serializers for specific use cases
class ApplicationDetailSerializer(ApplicationSerializer):
    """Extended serializer with more detailed information"""
    primary_server = ServerEnvironmentSerializer(read_only=True)
    additional_servers = ServerEnvironmentSerializer(many=True, read_only=True)
    
    class Meta(ApplicationSerializer.Meta):
        fields = ApplicationSerializer.Meta.fields


class ServerEnvironmentDetailSerializer(ServerEnvironmentSerializer):
    """Extended serializer with applications and installations"""
    primary_applications = ApplicationSerializer(many=True, read_only=True)
    additional_applications = ApplicationSerializer(many=True, read_only=True)
    language_installations = LanguageInstallationSerializer(many=True, read_only=True)
    datastore_instances = DataStoreInstanceSerializer(many=True, read_only=True)
    cloud_platform = CloudPlatformSerializer(read_only=True)
    
    class Meta(ServerEnvironmentSerializer.Meta):
        fields = ServerEnvironmentSerializer.Meta.fields
