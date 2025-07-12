"""
Serializers for auth app - user authentication and profile management.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes user profile information.
    
    Extends the default TokenObtainPairSerializer to include:
    - User profile information
    - User type and permissions
    - Directory information
    """
    
    def validate(self, attrs):
        """Validate credentials and return token with user info."""
        # Get the default token data
        data = super().validate(attrs)
        
        # Add custom user information
        user = self.user
        try:
            profile = user.profile
            data.update({
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
            })
            logger.info(f"User {user.username} logged in successfully")
        except UserProfile.DoesNotExist:
            logger.warning(f"User {user.username} logged in but has no profile")
            data.update({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff,
                'is_manager': False,
                'is_normal_user': True,
                'user_type': 'normal',
                'dir_name': f"user_{user.username}_{user.id}",
                'full_name': user.get_full_name() or user.username,
            })
        
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Handles user creation with password validation and profile setup.
    """
    
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        help_text="User password (must meet Django's password requirements)"
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True,
        help_text="Password confirmation"
    )
    email = serializers.EmailField(
        required=True,
        help_text="User email address"
    )
    
    class Meta:
        """Meta options for UserRegistrationSerializer."""
        model = User
        fields = (
            'username', 'password', 'password2', 'email', 
            'first_name', 'last_name'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """Create user and profile."""
        # Remove password2 from validated data
        validated_data.pop('password2')
        
        # Create user
        user = User.objects.create_user(**validated_data)
        logger.info(f"Created new user: {user.username}")
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.
    
    Provides read/write access to user profile fields.
    """
    
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    is_superuser = serializers.BooleanField(source='user.is_superuser', read_only=True)
    is_staff = serializers.BooleanField(source='user.is_staff', read_only=True)
    
    class Meta:
        """Meta options for UserProfileSerializer."""
        model = UserProfile
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_superuser', 'is_staff', 'is_manager', 'is_normal_user',
            'user_type', 'dir_name', 'full_name', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'dir_name')
    
    def update(self, instance, validated_data):
        """Update user profile with validation."""
        # Only allow managers and superusers to change user types
        user = self.context['request'].user
        if 'is_manager' in validated_data and not (user.is_superuser or user.profile.is_manager):
            raise serializers.ValidationError({
                "is_manager": "Only managers and superusers can change user types."
            })
        
        # Update the profile
        updated_profile = super().update(instance, validated_data)
        logger.info(f"Updated profile for user: {updated_profile.user.username}")
        
        return updated_profile


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    
    old_password = serializers.CharField(
        required=True,
        help_text="Current password"
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        help_text="New password (must meet Django's password requirements)"
    )
    new_password2 = serializers.CharField(
        required=True,
        help_text="New password confirmation"
    )
    
    def validate(self, attrs):
        """Validate password change request."""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "New password fields didn't match."
            })
        return attrs
    
    def validate_old_password(self, value):
        """Validate that old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def save(self):
        """Save the new password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        logger.info(f"Password changed for user: {user.username}")


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for user logout.
    """
    
    refresh_token = serializers.CharField(
        required=True,
        help_text="Refresh token to blacklist"
    )
    
    def validate_refresh_token(self, value):
        """Validate refresh token."""
        try:
            RefreshToken(value)
            return value
        except Exception as e:
            raise serializers.ValidationError("Invalid refresh token.")
    
    def save(self):
        """Blacklist the refresh token."""
        refresh_token = self.validated_data['refresh_token']
        token = RefreshToken(refresh_token)
        token.blacklist()
        logger.info("User logged out successfully") 