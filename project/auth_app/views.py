"""
Views for auth app - user authentication and profile management.
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf import settings
import logging

from .models import UserProfile
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    LogoutSerializer
)

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with enhanced user information.
    
    Extends the default TokenObtainPairView to include user profile data
    in the response.
    """
    
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        """Handle login request with enhanced logging."""
        try:
            response = super().post(request, *args, **kwargs)
            logger.info(f"Login successful for user: {request.data.get('username', 'unknown')}")
            return response
        except Exception as e:
            logger.error(f"Login failed for user: {request.data.get('username', 'unknown')} - {str(e)}")
            raise


class UserRegistrationView(generics.CreateAPIView):
    """
    View for user registration.
    
    Allows new users to register with automatic profile creation.
    """
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Create new user with profile."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            # Get the created profile
            profile = user.profile
            
            # Create user directory
            import os
            user_dir = os.path.join(settings.MASTER_DIR, profile.dir_name)
            os.makedirs(user_dir, exist_ok=True)
            logger.info(f"Created user directory: {user_dir}")
            
            return Response({
                'message': 'User registered successfully',
                'user_id': user.id,
                'username': user.username,
                'dir_name': profile.dir_name
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"User registration failed: {str(e)}")
            return Response({
                'error': 'Registration failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View for user profile management.
    
    Allows users to view and update their profile information.
    """
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get the current user's profile."""
        return self.request.user.profile
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve user profile with logging."""
        try:
            profile = self.get_object()
            serializer = self.get_serializer(profile)
            logger.debug(f"Profile retrieved for user: {request.user.username}")
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            logger.warning(f"Profile not found for user: {request.user.username}")
            return Response({
                'error': 'Profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def update(self, request, *args, **kwargs):
        """Update user profile with validation."""
        try:
            profile = self.get_object()
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            logger.info(f"Profile updated for user: {request.user.username}")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Profile update failed for user: {request.user.username} - {str(e)}")
            return Response({
                'error': 'Profile update failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    View for changing user password.
    
    Allows authenticated users to change their password.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Change user password."""
        try:
            serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            logger.info(f"Password changed for user: {request.user.username}")
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Password change failed for user: {request.user.username} - {str(e)}")
            return Response({
                'error': 'Password change failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    View for user logout.
    
    Blacklists the refresh token to invalidate the session.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Logout user by blacklisting refresh token."""
        try:
            serializer = LogoutSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            logger.info(f"User logged out: {request.user.username}")
            return Response({
                'message': 'Logged out successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Logout failed for user: {request.user.username} - {str(e)}")
            return Response({
                'error': 'Logout failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    """
    View for listing users (managers and superusers only).
    
    Provides a list of all users with their profile information.
    """
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get queryset based on user permissions."""
        user = self.request.user
        
        # Only managers and superusers can list users
        if not (user.is_superuser or user.profile.is_manager):
            logger.warning(f"Unauthorized access attempt to user list by: {user.username}")
            return UserProfile.objects.none()
        
        logger.info(f"User list accessed by: {user.username}")
        return UserProfile.objects.all().select_related('user')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_info(request):
    """
    Get current user information.
    
    Returns detailed information about the currently authenticated user.
    """
    try:
        user = request.user
        profile = user.profile
        
        data = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'is_manager': profile.is_manager,
            'is_normal_user': profile.is_normal_user,
            'user_type': profile.user_type,
            'dir_name': profile.dir_name,
            'full_name': profile.full_name,
            'created_at': profile.created_at,
            'updated_at': profile.updated_at,
        }
        
        logger.debug(f"User info retrieved for: {user.username}")
        return Response(data)
        
    except UserProfile.DoesNotExist:
        logger.warning(f"Profile not found for user: {request.user.username}")
        return Response({
            'error': 'Profile not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error retrieving user info for {request.user.username}: {str(e)}")
        return Response({
            'error': 'Failed to retrieve user information',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_auth(request):
    """
    Test endpoint for authentication.
    
    Simple endpoint to test if JWT authentication is working.
    """
    logger.debug(f"Auth test endpoint accessed by: {request.user.username}")
    return Response({
        'message': 'Authentication successful',
        'user': request.user.username,
        'user_type': request.user.profile.user_type
    })
