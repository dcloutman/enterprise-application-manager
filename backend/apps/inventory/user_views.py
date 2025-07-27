from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import UserProfile, RecordPermission
from .user_serializers import UserProfileSerializer, UserCreateSerializer, RecordPermissionSerializer
from .permissions import IsApplicationAdmin, CanManageUsers


class UserListCreateView(generics.ListCreateAPIView):
    """List all users or create a new user with profile (Application Admin only)"""
    queryset = User.objects.all().select_related('profile')
    permission_classes = [permissions.IsAuthenticated, CanManageUsers]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserProfileSerializer
    
    def get_queryset(self):
        """Filter users based on requesting user's role"""
        user = self.request.user
        if hasattr(user, 'profile'):
            if user.profile.role == 'application_admin':
                # Application Admins can see all users
                return User.objects.all().select_related('profile')
            elif user.profile.role == 'systems_manager':
                # Systems Managers can see all non-admin users
                return User.objects.exclude(profile__role='application_admin').select_related('profile')
        return User.objects.none()
    
    @transaction.atomic
    def perform_create(self, serializer):
        """Create user and associated profile"""
        user = serializer.save()
        # UserProfile is created via the serializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a specific user (Application Admin only)"""
    queryset = User.objects.all().select_related('profile')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageUsers]
    
    def get_queryset(self):
        """Filter users based on requesting user's role"""
        user = self.request.user
        if hasattr(user, 'profile'):
            if user.profile.role == 'application_admin':
                return User.objects.all().select_related('profile')
            elif user.profile.role == 'systems_manager':
                return User.objects.exclude(profile__role='application_admin').select_related('profile')
        return User.objects.none()


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """View and update user profile information"""
    queryset = UserProfile.objects.all().select_related('user')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Users can only view/edit their own profile unless they're admin"""
        user = self.request.user
        profile_id = self.kwargs.get('pk')
        
        if hasattr(user, 'profile') and user.profile.can_manage_users():
            # Application Admins can edit any profile
            return get_object_or_404(UserProfile, pk=profile_id)
        else:
            # Regular users can only edit their own profile
            return get_object_or_404(UserProfile, pk=profile_id, user=user)


class RecordPermissionListCreateView(generics.ListCreateAPIView):
    """List and create record permissions (Systems Managers and Application Admins only)"""
    queryset = RecordPermission.objects.all().select_related('user', 'granted_by', 'content_type')
    serializer_class = RecordPermissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsApplicationAdmin]
    
    def perform_create(self, serializer):
        serializer.save(granted_by=self.request.user)


class RecordPermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete record permissions"""
    queryset = RecordPermission.objects.all().select_related('user', 'granted_by', 'content_type')
    serializer_class = RecordPermissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsApplicationAdmin]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user_profile(request):
    """Get the current user's profile information"""
    try:
        profile = request.user.profile
        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)
    except UserProfile.DoesNotExist:
        # Create a default profile if none exists
        profile = UserProfile.objects.create(
            user=request.user,
            role='business_user'
        )
        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_permissions_summary(request):
    """Get a summary of the current user's permissions"""
    try:
        profile = request.user.profile
        return Response({
            'user_id': request.user.id,
            'username': request.user.username,
            'role': profile.role,
            'role_display': profile.get_role_display(),
            'permissions': {
                'can_manage_users': profile.can_manage_users(),
                'can_view_system_notes': profile.can_view_system_notes(),
                'can_create_records': profile.can_create_records(),
                'can_delete_records': profile.can_delete_records(),
                'has_write_access': profile.has_write_access(),
            },
            'department': profile.department,
            'is_active': profile.is_active,
        })
    except UserProfile.DoesNotExist:
        # Return minimal permissions for users without profiles
        return Response({
            'user_id': request.user.id,
            'username': request.user.username,
            'role': 'business_user',
            'role_display': 'Business User',
            'permissions': {
                'can_manage_users': False,
                'can_view_system_notes': False,
                'can_create_records': False,
                'can_delete_records': False,
                'has_write_access': False,
            },
            'department': '',
            'is_active': True,
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, CanManageUsers])
def assign_record_permission(request):
    """Assign specific record permissions to users"""
    serializer = RecordPermissionSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(granted_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated, CanManageUsers])
def revoke_record_permission(request, permission_id):
    """Revoke a specific record permission"""
    try:
        permission = RecordPermission.objects.get(id=permission_id)
        permission.delete()
        return Response({'message': 'Permission revoked successfully'}, status=status.HTTP_204_NO_CONTENT)
    except RecordPermission.DoesNotExist:
        return Response({'error': 'Permission not found'}, status=status.HTTP_404_NOT_FOUND)
