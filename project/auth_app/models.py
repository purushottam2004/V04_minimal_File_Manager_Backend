"""
Auth app models for user management and authentication.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


class UserProfile(models.Model):
    """
    Extended user profile model with custom fields for file manager access.
    
    This model extends Django's built-in User model to add:
    - is_manager: Boolean field for manager role
    - is_normal_user: Boolean field for normal user role  
    - dir_name: String field for user's assigned directory
    """
    
    # User types
    USER_TYPE_CHOICES = [
        ('normal', 'Normal User'),
        ('manager', 'Manager'),
        ('superuser', 'Superuser'),
    ]
    
    # Link to Django's built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Custom fields
    is_manager = models.BooleanField(default=False, help_text="Designates if this user is a manager")
    is_normal_user = models.BooleanField(default=True, help_text="Designates if this user is a normal user")
    dir_name = models.CharField(
        max_length=255, 
        unique=True, 
        help_text="Directory name assigned to this user"
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='normal',
        help_text="Type of user (normal, manager, superuser)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for UserProfile model."""
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        db_table = 'auth_user_profile'
    
    def __str__(self) -> str:
        """String representation of UserProfile."""
        return f"{self.user.username} - {self.user_type}"
    
    def save(self, *args, **kwargs) -> None:
        """Override save method to add logging and validation."""
        if hasattr(self, '_state') and self._state.adding:
            logger.info(f"Creating new user profile for user: {self.user.username}")
        else:
            logger.info(f"Updating user profile for user: {self.user.username}")
        
        # Ensure user type consistency
        if self.user.is_superuser:
            self.user_type = 'superuser'
            self.is_manager = False
            self.is_normal_user = False
        elif self.is_manager:
            self.user_type = 'manager'
            self.is_normal_user = False
        else:
            self.user_type = 'normal'
            self.is_normal_user = True
            self.is_manager = False
        
        super().save(*args, **kwargs)
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    @property
    def user_directory_path(self) -> str:
        """Get the full path to user's directory."""
        from django.conf import settings
        import os
        return os.path.join(settings.MASTER_DIR, self.dir_name)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create UserProfile when User is created.
    
    Args:
        sender: The User model class
        instance: The User instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        # Generate directory name based on username
        dir_name = f"user_{instance.username}_{instance.id}"
        
        # Create user profile
        UserProfile.objects.create(
            user=instance,
            dir_name=dir_name,
            is_normal_user=True,
            is_manager=False
        )
        logger.info(f"Created user profile for new user: {instance.username}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler to automatically save UserProfile when User is saved.
    
    Args:
        sender: The User model class
        instance: The User instance being saved
        **kwargs: Additional keyword arguments
    """
    try:
        instance.profile.save()
        logger.debug(f"Saved user profile for user: {instance.username}")
    except UserProfile.DoesNotExist:
        # If profile doesn't exist, create it
        dir_name = f"user_{instance.username}_{instance.id}"
        UserProfile.objects.create(
            user=instance,
            dir_name=dir_name,
            is_normal_user=True,
            is_manager=False
        )
        logger.info(f"Created missing user profile for user: {instance.username}")
