from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth import authenticate
from .models import CustomUser, UserProfile, PasswordReset, EmailVerification, FirebaseApp, FcmDevice, PushNotification

class CustomUserCreationForm(UserCreationForm):
    """Enhanced user registration form"""
    
    # Additional fields for registration
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your last name'
        })
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+1234567890'
        })
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        })
    )
    
    # Override email field
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address'
        })
    )
    
    # Override password fields
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password'
        }),
        help_text='Password must be at least 8 characters long and contain letters and numbers.'
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your password'
        })
    )
    
    # Terms and conditions
    agree_to_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        error_messages={'required': 'You must agree to the terms and conditions.'}
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make username field required
        self.fields['username'].required = True
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Choose a username'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already registered.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data.get('phone_number', '')
        user.date_of_birth = self.cleaned_data.get('date_of_birth')
        
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    """Enhanced user profile update form"""
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 'bio', 'website', 'location')

class CustomAuthenticationForm(AuthenticationForm):
    """Enhanced login form with security features"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email or username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        initial=True
    )
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Try to authenticate with email or username
            user = authenticate(username=username, password=password)
            if user is None:
                # Try with email
                try:
                    user_obj = CustomUser.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    pass
            
            if user is None:
                raise forms.ValidationError('Invalid email/username or password.')
            else:
                # Check if account is locked
                if user.is_account_locked:
                    raise forms.ValidationError('Your account is temporarily locked due to multiple failed login attempts. Please try again later.')
                
                # Check if account is active
                if not user.is_active:
                    raise forms.ValidationError('Your account is disabled. Please contact support.')
                
                self.user_cache = user
                # Reset failed login attempts on successful login
                user.reset_failed_login_attempts()
        
        return self.cleaned_data

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'phone_number', 'date_of_birth',
            'profile_picture', 'bio', 'website', 'location',
            'github', 'linkedin', 'twitter', 'instagram', 'facebook',
            'timezone', 'language', 'theme'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-file'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'website': forms.URLInput(attrs={'class': 'form-input'}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
            'github': forms.URLInput(attrs={'class': 'form-input'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-input'}),
            'twitter': forms.URLInput(attrs={'class': 'form-input'}),
            'instagram': forms.URLInput(attrs={'class': 'form-input'}),
            'facebook': forms.URLInput(attrs={'class': 'form-input'}),
            'timezone': forms.Select(attrs={'class': 'form-select'}),
            'language': forms.Select(attrs={'class': 'form-select'}),
            'theme': forms.Select(attrs={'class': 'form-select'}),
        }

class PasswordChangeForm(forms.Form):
    """Custom password change form"""
    
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your current password'
        })
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your new password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your new password'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Current password is incorrect.')
        return current_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('New passwords do not match.')
        
        return cleaned_data

class EmailVerificationForm(forms.Form):
    """Email verification form"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('No account found with this email address.')
        return email

class PasswordResetRequestForm(forms.Form):
    """Password reset request form"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('No account found with this email address.')
        return email

class PasswordResetConfirmForm(forms.Form):
    """Password reset confirmation form"""
    
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your new password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your new password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        
        return cleaned_data

class AccountDeactivationForm(forms.Form):
    """Account deactivation form"""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password to confirm'
        })
    )
    confirm_deactivation = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        error_messages={'required': 'You must confirm that you want to deactivate your account.'}
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError('Password is incorrect.')
        return password

# Firebase Forms
class FirebaseAppForm(forms.ModelForm):
    """Form for creating/editing Firebase apps"""
    
    class Meta:
        model = FirebaseApp
        fields = ['name', 'project_id', 'project_name', 'service_account_file', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter app name (e.g., MyApp)'
            }),
            'project_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter Firebase project ID (e.g., my-project-123)'
            }),
            'project_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter project name (optional)'
            }),
            'service_account_file': forms.FileInput(attrs={
                'class': 'form-file',
                'accept': '.json'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            })
        }
    
    def clean_project_id(self):
        project_id = self.cleaned_data.get('project_id')
        if project_id:
            # Basic validation for Firebase project ID format
            if not project_id.replace('-', '').replace('_', '').isalnum():
                raise forms.ValidationError('Project ID can only contain letters, numbers, hyphens, and underscores.')
        return project_id
    
    def clean_service_account_file(self):
        file = self.cleaned_data.get('service_account_file')
        if file:
            # Check file extension
            if not file.name.endswith('.json'):
                raise forms.ValidationError('Service account file must be a JSON file.')
            
            # Check file size (max 1MB)
            if file.size > 1024 * 1024:
                raise forms.ValidationError('Service account file size must be less than 1MB.')
            
            # Try to parse JSON to validate
            try:
                import json
                file.seek(0)
                json.load(file)
                file.seek(0)  # Reset file pointer
            except json.JSONDecodeError:
                raise forms.ValidationError('Invalid JSON file. Please upload a valid service account JSON file.')
        
        return file

class FcmDeviceForm(forms.ModelForm):
    """Form for adding FCM devices"""
    
    class Meta:
        model = FcmDevice
        fields = ['token', 'device_id', 'device_type']
        widgets = {
            'token': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter FCM token (starts with fcm...)'
            }),
            'device_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter device identifier (optional)'
            }),
            'device_type': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def clean_token(self):
        token = self.cleaned_data.get('token')
        if token:
            # Remove any whitespace
            token = token.strip()
            
            # Basic validation for FCM token format
            # Modern FCM tokens can start with various prefixes
            valid_prefixes = ['fcm', 'APA', 'cSMQwCvFT8yZEP_mpqPsu_']
            
            # Check if token starts with any valid prefix or has proper length
            is_valid = False
            
            # Check for known prefixes
            for prefix in valid_prefixes:
                if token.startswith(prefix):
                    is_valid = True
                    break
            
            # If no known prefix, check if it's a valid length (FCM tokens are typically 140-160 characters)
            if not is_valid and len(token) >= 100 and len(token) <= 200:
                is_valid = True
            
            if not is_valid:
                raise forms.ValidationError(
                    'Invalid FCM token format. Token should be a valid Firebase Cloud Messaging token.'
                )
            
            return token
        return token

class PushNotificationForm(forms.ModelForm):
    """Form for sending push notifications"""
    
    # Additional fields for token input
    token_input = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 3,
            'placeholder': 'Enter FCM tokens (one per line) or leave empty to send to all devices'
        }),
        help_text='Enter FCM tokens separated by new lines, or leave empty to send to all registered devices.'
    )
    
    # Additional fields for device selection
    send_to_all = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        help_text='Send to all registered devices for this app'
    )
    
    class Meta:
        model = PushNotification
        fields = ['title', 'body', 'image_url', 'data', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter notification title'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Enter notification message'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter image URL (optional)'
            }),
            'data': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': 'Enter custom data as JSON (optional)'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def clean_data(self):
        data = self.cleaned_data.get('data')
        if data:
            try:
                import json
                if isinstance(data, str):
                    json.loads(data)
                elif isinstance(data, dict):
                    json.dumps(data)  # Test if it's serializable
            except (json.JSONDecodeError, TypeError):
                raise forms.ValidationError('Custom data must be valid JSON.')
        return data
    
    def clean(self):
        cleaned_data = super().clean()
        send_to_all = cleaned_data.get('send_to_all')
        token_input = cleaned_data.get('token_input')
        
        if not send_to_all and not token_input:
            raise forms.ValidationError('Either select "Send to all devices" or provide specific tokens.')
        
        return cleaned_data 