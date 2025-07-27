from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create API router
router = DefaultRouter()
router.register(r'cloud-platforms', views.CloudPlatformViewSet)
router.register(r'servers', views.ServerEnvironmentViewSet)
router.register(r'languages', views.LanguageViewSet)
router.register(r'datastores', views.DataStoreViewSet)
router.register(r'language-installations', views.LanguageInstallationViewSet)
router.register(r'datastore-instances', views.DataStoreInstanceViewSet)
router.register(r'applications', views.ApplicationViewSet)
router.register(r'application-language-dependencies', views.ApplicationLanguageDependencyViewSet)
router.register(r'application-datastore-dependencies', views.ApplicationDataStoreDependencyViewSet)
router.register(r'application-lifecycle-events', views.ApplicationLifecycleEventViewSet)
router.register(r'cloud-plugins', views.CloudPluginViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
