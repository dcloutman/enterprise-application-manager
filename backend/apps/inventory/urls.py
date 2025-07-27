from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, user_views

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
    
    # User Management URLs
    path('api/users/', user_views.UserListCreateView.as_view(), name='user-list-create'),
    path('api/users/<int:pk>/', user_views.UserDetailView.as_view(), name='user-detail'),
    path('api/user-profiles/<int:pk>/', user_views.UserProfileDetailView.as_view(), name='userprofile-detail'),
    path('api/record-permissions/', user_views.RecordPermissionListCreateView.as_view(), name='recordpermission-list-create'),
    path('api/record-permissions/<int:pk>/', user_views.RecordPermissionDetailView.as_view(), name='recordpermission-detail'),
    
    # User Authentication & Profile URLs
    path('api/auth/profile/', user_views.current_user_profile, name='current-user-profile'),
    path('api/auth/permissions/', user_views.user_permissions_summary, name='user-permissions-summary'),
    path('api/auth/assign-permission/', user_views.assign_record_permission, name='assign-record-permission'),
    path('api/auth/revoke-permission/<int:permission_id>/', user_views.revoke_record_permission, name='revoke-record-permission'),
]
