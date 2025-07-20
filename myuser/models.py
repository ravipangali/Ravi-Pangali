from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
import os

class CustomUserManager(BaseUserManager):
    """Custom user manager for creating users and superusers"""
    
    def create_user(self, email, username, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, username, password, **extra_fields)

class CustomUser(AbstractUser):
    """Enhanced custom user model with comprehensive authentication features"""
    
    # User identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name='Email Address')
    username = models.CharField(max_length=150, unique=True, verbose_name='Username')
    
    # Personal information
    first_name = models.CharField(max_length=30, verbose_name='First Name')
    last_name = models.CharField(max_length=30, verbose_name='Last Name')
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        verbose_name='Phone Number'
    )
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='Date of Birth')
    
    # Profile information
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        blank=True, 
        null=True,
        verbose_name='Profile Picture'
    )
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name='Bio')
    website = models.URLField(blank=True, null=True, verbose_name='Website')
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name='Location')
    
    # Social media links
    github = models.URLField(blank=True, null=True, verbose_name='GitHub')
    linkedin = models.URLField(blank=True, null=True, verbose_name='LinkedIn')
    twitter = models.URLField(blank=True, null=True, verbose_name='Twitter')
    instagram = models.URLField(blank=True, null=True, verbose_name='Instagram')
    facebook = models.URLField(blank=True, null=True, verbose_name='Facebook')
    
    # Account status and verification
    is_verified = models.BooleanField(default=False, verbose_name='Email Verified')
    is_premium = models.BooleanField(default=False, verbose_name='Premium User')
    is_beta_tester = models.BooleanField(default=False, verbose_name='Beta Tester')
    
    # Security and tracking
    last_login_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name='Last Login IP')
    last_login_location = models.CharField(max_length=100, blank=True, null=True, verbose_name='Last Login Location')
    failed_login_attempts = models.PositiveIntegerField(default=0, verbose_name='Failed Login Attempts')
    account_locked_until = models.DateTimeField(blank=True, null=True, verbose_name='Account Locked Until')
    
    # User preferences
    timezone = models.CharField(max_length=50, default='UTC', verbose_name='Timezone')
    language = models.CharField(max_length=10, default='en', verbose_name='Language')
    theme = models.CharField(max_length=20, default='light', verbose_name='Theme')
    email_notifications = models.BooleanField(default=True, verbose_name='Email Notifications')
    push_notifications = models.BooleanField(default=True, verbose_name='Push Notifications')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='Last Activity')
    
    # Email verification
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(blank=True, null=True)
    
    # Password reset
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_sent_at = models.DateTimeField(blank=True, null=True)
    
    objects = CustomUserManager()
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    @property
    def display_name(self):
        """Return the display name (full name or username)"""
        if self.get_full_name():
            return self.get_full_name()
        return self.username
    
    @property
    def is_account_locked(self):
        """Check if account is currently locked"""
        if self.account_locked_until and self.account_locked_until > timezone.now():
            return True
        return False
    
    def increment_failed_login(self):
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            # Lock account for 30 minutes
            self.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save()
    
    def reset_failed_login_attempts(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save()
    
    def generate_email_verification_token(self):
        """Generate email verification token"""
        import secrets
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_sent_at = timezone.now()
        self.save()
        return self.email_verification_token
    
    def generate_password_reset_token(self):
        """Generate password reset token"""
        import secrets
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_sent_at = timezone.now()
        self.save()
        return self.password_reset_token
    
    def verify_email(self, token):
        """Verify email with token"""
        if (self.email_verification_token == token and 
            self.email_verification_sent_at and 
            timezone.now() - self.email_verification_sent_at < timezone.timedelta(hours=24)):
            self.is_verified = True
            self.email_verification_token = None
            self.email_verification_sent_at = None
            self.save()
            return True
        return False
    
    def reset_password(self, token, new_password):
        """Reset password with token"""
        if (self.password_reset_token == token and 
            self.password_reset_sent_at and 
            timezone.now() - self.password_reset_sent_at < timezone.timedelta(hours=1)):
            self.set_password(new_password)
            self.password_reset_token = None
            self.password_reset_sent_at = None
            self.save()
            return True
        return False

class UserProfile(models.Model):
    """Extended user profile information"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    
    # Professional information
    job_title = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    skills = models.JSONField(default=list, blank=True)
    
    # Preferences
    notification_preferences = models.JSONField(default=dict)
    privacy_settings = models.JSONField(default=dict)
    
    # Statistics
    login_count = models.PositiveIntegerField(default=0)
    last_login_date = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class EmailVerification(models.Model):
    """Email verification tokens"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='email_verifications')
    token = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        verbose_name = "Email Verification"
        verbose_name_plural = "Email Verifications"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.email}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at

class PasswordReset(models.Model):
    """Password reset tokens"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='password_resets')
    token = models.CharField(max_length=100, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        verbose_name = "Password Reset"
        verbose_name_plural = "Password Resets"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at

class FirebaseApp(models.Model):
    """Firebase App configuration for push notifications"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='firebase_apps')
    name = models.CharField(max_length=100, verbose_name='App Name')
    project_id = models.CharField(max_length=100, verbose_name='Firebase Project ID')
    project_name = models.CharField(max_length=100, verbose_name='Project Name', blank=True, null=True)
    service_account_file = models.FileField(
        upload_to='firebase_services/', 
        verbose_name='Service Account JSON File'
    )
    is_active = models.BooleanField(default=True, verbose_name='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Firebase App"
        verbose_name_plural = "Firebase Apps"
        ordering = ['-created_at']
        unique_together = [['user', 'name']]
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def get_service_account_path(self):
        """Get the full path to the service account file"""
        if self.service_account_file:
            return self.service_account_file.path
        return None

class FcmDevice(models.Model):
    """FCM Device tokens for push notifications"""
    DEVICE_TYPE_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web'),
        ('unknown', 'Unknown'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firebase_app = models.ForeignKey(FirebaseApp, on_delete=models.CASCADE, related_name='devices')
    token = models.CharField(max_length=500, unique=True, verbose_name='FCM Token')
    device_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='Device ID')
    device_type = models.CharField(
        max_length=20, 
        choices=DEVICE_TYPE_CHOICES, 
        default='unknown', 
        verbose_name='Device Type'
    )
    is_active = models.BooleanField(default=True, verbose_name='Active')
    last_used = models.DateTimeField(auto_now=True, verbose_name='Last Used')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "FCM Device"
        verbose_name_plural = "FCM Devices"
        ordering = ['-created_at']
        unique_together = [['firebase_app', 'token']]
    
    def __str__(self):
        return f"{self.firebase_app.name} - {self.device_type} - {self.token[:20]}..."

class PushNotification(models.Model):
    """Push notification records"""
    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firebase_app = models.ForeignKey(FirebaseApp, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255, verbose_name='Notification Title')
    body = models.TextField(verbose_name='Notification Body')
    image_url = models.URLField(blank=True, null=True, verbose_name='Image URL')
    data = models.JSONField(default=dict, verbose_name='Custom Data')
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='high', 
        verbose_name='Priority'
    )
    # New fields for enhanced notification features
    notification_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='Notification Type')
    sound = models.CharField(max_length=50, blank=True, null=True, verbose_name='Sound')
    data_only = models.BooleanField(default=False, verbose_name='Data Only')
    is_alarm = models.BooleanField(default=False, verbose_name='Is Alarm')
    urgent = models.BooleanField(default=False, verbose_name='Urgent')
    persistent = models.BooleanField(default=False, verbose_name='Persistent')
    tokens_sent = models.PositiveIntegerField(default=0, verbose_name='Tokens Sent')
    tokens_delivered = models.PositiveIntegerField(default=0, verbose_name='Tokens Delivered')
    tokens_failed = models.PositiveIntegerField(default=0, verbose_name='Tokens Failed')
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Push Notification"
        verbose_name_plural = "Push Notifications"
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.firebase_app.name} - {self.title} - {self.sent_at}"

# Signal handlers
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a user is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Save the user profile when the user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
