"""
Admin configuration for auth app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile model.
    
    Displays UserProfile fields inline with User admin.
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    """
    Custom User admin that includes UserProfile inline.
    
    Extends the default UserAdmin to include profile information.
    """
    inlines = (UserProfileInline,)
    
    def get_inline_instances(self, request, obj=None):
        """Get inline instances for the admin."""
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserProfile model.
    
    Provides detailed admin interface for managing user profiles.
    """
    list_display = ('user', 'user_type', 'dir_name', 'is_manager', 'is_normal_user', 'created_at')
    list_filter = ('user_type', 'is_manager', 'is_normal_user', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'dir_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'user_type', 'dir_name')
        }),
        ('Permissions', {
            'fields': ('is_manager', 'is_normal_user')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with user information."""
        return super().get_queryset(request).select_related('user')
