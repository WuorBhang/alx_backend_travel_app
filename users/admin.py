from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = [
        'phone_number', 'date_of_birth', 'address', 'city', 'country', 'postal_code',
        'preferred_trip_types', 'preferred_destinations', 'budget_range',
        'email_notifications', 'sms_notifications', 'marketing_emails'
    ]


class UserAdmin(BaseUserAdmin):
    """Custom User admin with profile inline"""
    inlines = (UserProfileInline,)
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'is_staff', 
        'is_active', 'date_joined'
    ]
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['username']


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model"""
    list_display = [
        'user', 'full_name', 'phone_number', 'city', 'country', 
        'budget_range', 'has_complete_profile'
    ]
    list_filter = [
        'budget_range', 'email_notifications', 'sms_notifications', 
        'marketing_emails', 'country', 'created_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'user__first_name', 
        'user__last_name', 'phone_number', 'city', 'country'
    ]
    readonly_fields = ['full_name', 'has_complete_profile', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name')
        }),
        ('Personal Information', {
            'fields': ('phone_number', 'date_of_birth', 'address', 'city', 'country', 'postal_code')
        }),
        ('Travel Preferences', {
            'fields': ('preferred_trip_types', 'preferred_destinations', 'budget_range')
        }),
        ('Notification Settings', {
            'fields': ('email_notifications', 'sms_notifications', 'marketing_emails')
        }),
        ('Profile Status', {
            'fields': ('has_complete_profile', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Show all profiles with related user data"""
        return super().get_queryset(request).select_related('user')
