from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    CustomUser, UserProfile, EmailVerification, PasswordReset, FirebaseApp, FcmDevice, PushNotification
)

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Enhanced admin interface for CustomUser"""

    list_display = [
        'id','username', 'email', 'full_name', 'is_verified', 'is_active',
        'is_premium', 'last_login', 'created_at', 'status_badge'
    ]
    list_filter = [
        'is_verified', 'is_active', 'is_premium', 'is_beta_tester',
        'is_staff', 'is_superuser', 'created_at', 'last_login'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_activity']

    fieldsets = (
        ('User Information', {
            'fields': ('id', 'username', 'email', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone_number', 'date_of_birth')
        }),
        ('Profile Information', {
            'fields': ('profile_picture', 'bio', 'website', 'location')
        }),
        ('Social Media', {
            'fields': ('github', 'linkedin', 'twitter', 'instagram', 'facebook'),
            'classes': ('collapse',)
        }),
        ('Account Status', {
            'fields': ('is_active', 'is_verified', 'is_premium', 'is_beta_tester', 'is_staff', 'is_superuser')
        }),
        ('Security', {
            'fields': ('last_login_ip', 'last_login_location', 'failed_login_attempts', 'account_locked_until'),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('timezone', 'language', 'theme', 'email_notifications', 'push_notifications'),       
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

    def full_name(self, obj):
        """Display full name"""
        return obj.get_full_name()
    full_name.short_description = 'Full Name'

    def status_badge(self, obj):
        """Display status badges"""
        badges = []
        if obj.is_verified:
            badges.append('<span class="badge badge-success">Verified</span>')
        if obj.is_premium:
            badges.append('<span class="badge badge-warning">Premium</span>')
        if obj.is_beta_tester:
            badges.append('<span class="badge badge-info">Beta</span>')
        if obj.is_account_locked:
            badges.append('<span class="badge badge-danger">Locked</span>')
        return mark_safe(' '.join(badges))
    status_badge.short_description = 'Status'

    def get_queryset(self, request):
        """Optimize queryset with related fields"""
        return super().get_queryset(request).select_related('profile')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile"""

    list_display = ['user', 'job_title', 'company', 'login_count', 'last_login_date']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'job_title', 'company']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Profile Information', {
            'fields': ('id', 'user')
        }),
        ('Professional Information', {
            'fields': ('job_title', 'company', 'industry', 'skills')
        }),
        ('Preferences', {
            'fields': ('notification_preferences', 'privacy_settings'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('login_count', 'last_login_date'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    """Admin interface for EmailVerification"""

    list_display = ['user', 'email', 'is_used', 'created_at', 'expires_at', 'is_expired']
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'email', 'token']
    readonly_fields = ['id', 'created_at', 'expires_at']

    fieldsets = (
        ('Verification Information', {
            'fields': ('id', 'user', 'email', 'token', 'is_used')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at')
        }),
    )

    def is_expired(self, obj):
        """Check if verification is expired"""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'

@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    """Admin interface for PasswordReset"""

    list_display = ['user', 'is_used', 'created_at', 'expires_at', 'is_expired']
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'token']
    readonly_fields = ['id', 'created_at', 'expires_at']

    fieldsets = (
        ('Reset Information', {
            'fields': ('id', 'user', 'token', 'is_used')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at')
        }),
    )

    def is_expired(self, obj):
        """Check if reset is expired"""
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'

# --- New admin registrations for remaining models ---

@admin.register(FirebaseApp)
class FirebaseAppAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'user', 'project_id', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['name', 'project_id', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(FcmDevice)
class FcmDeviceAdmin(admin.ModelAdmin):
    list_display = ['token_preview', 'firebase_app', 'device_type', 'is_active', 'last_used', 'created_at']
    list_filter = ['device_type', 'is_active', 'created_at']
    search_fields = ['token', 'device_id', 'firebase_app__name']
    readonly_fields = ['created_at', 'last_used']
    ordering = ['-created_at']

    def token_preview(self, obj):
        return obj.token[:20] + '...' if len(obj.token) > 20 else obj.token
    token_preview.short_description = 'Token'

@admin.register(PushNotification)
class PushNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'firebase_app', 'priority', 'tokens_sent', 'tokens_delivered', 'tokens_failed', 'sent_at']
    list_filter = ['priority', 'sent_at']
    search_fields = ['title', 'firebase_app__name', 'body']
    readonly_fields = ['sent_at']
    ordering = ['-sent_at']

# Custom admin site configuration
admin.site.site_header = "Ravi Pangali Admin"
admin.site.site_title = "Ravi Pangali Admin Portal"
admin.site.index_title = "Welcome to Ravi Pangali Administration"

# Custom admin actions
@admin.action(description="Mark selected users as verified")
def mark_users_verified(modeladmin, request, queryset):
    queryset.update(is_verified=True)
mark_users_verified.short_description = "Mark selected users as verified"

@admin.action(description="Mark selected users as premium")
def mark_users_premium(modeladmin, request, queryset):
    queryset.update(is_premium=True)
mark_users_premium.short_description = "Mark selected users as premium"
