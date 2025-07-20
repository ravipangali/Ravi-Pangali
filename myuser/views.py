from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.db.models import Q, Sum
import json
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, 
    PasswordChangeForm, PasswordResetRequestForm, PasswordResetConfirmForm,
    FirebaseAppForm, FcmDeviceForm, PushNotificationForm
)
from .models import CustomUser, PasswordReset, EmailVerification, FirebaseApp, FcmDevice, PushNotification
from .firebase_service import get_firebase_service, test_firebase_app

# Django REST Framework imports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

import secrets
from datetime import timedelta
from .models import (
    CustomUser, UserProfile, EmailVerification, PasswordReset,
    FirebaseApp, FcmDevice, PushNotification
)
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm,
    PasswordChangeForm, EmailVerificationForm, PasswordResetRequestForm,
    PasswordResetConfirmForm, AccountDeactivationForm,
    FirebaseAppForm, FcmDeviceForm, PushNotificationForm
)
from .firebase_service import get_firebase_service, test_firebase_app

def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Try to authenticate with username or email
            user = authenticate(username=username, password=password)
            if user is None:
                # Try with email if username didn't work
                try:
                    user_obj = CustomUser.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    pass

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.display_name}!')

                # Redirect to next page or home
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username/email or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomAuthenticationForm()

    context = {
        'form': form,
        'title': 'Login - Ravi Pangali'
    }
    return render(request, 'myuser/login.html', context)

def register_view(request):
    # Registration is currently disabled
    messages.error(request, 'User registration is currently disabled.')
    return redirect('myuser:login')

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def profile_view(request):
    """Handle user profile view and edit"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('myuser:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user)

    context = {
        'form': form,
        'title': 'Profile - Ravi Pangali'
    }
    return render(request, 'myuser/profile.html', context)

@login_required
def dashboard_view(request):
    """User dashboard"""
    # Get Firebase stats
    firebase_stats = {
        'total_apps': FirebaseApp.objects.filter(user=request.user).count(),
        'total_devices': FcmDevice.objects.filter(firebase_app__user=request.user).count(),
        'total_notifications': PushNotification.objects.filter(firebase_app__user=request.user).count(),
        'success_rate': 0
    }
    
    # Calculate success rate
    total_sent = PushNotification.objects.filter(firebase_app__user=request.user).aggregate(
        total=Sum('tokens_sent')
    )['total'] or 0
    total_delivered = PushNotification.objects.filter(firebase_app__user=request.user).aggregate(
        total=Sum('tokens_delivered')
    )['total'] or 0
    
    if total_sent > 0:
        firebase_stats['success_rate'] = round((total_delivered / total_sent) * 100, 1)
    
    context = {
        'title': 'Dashboard - Ravi Pangali',
        'firebase_stats': firebase_stats,
    }
    return render(request, 'myuser/dashboard.html', context)

@login_required
def password_change_view(request):
    """Handle password change"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('myuser:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    context = {
        'form': form,
        'title': 'Change Password - Ravi Pangali'
    }
    return render(request, 'myuser/password_change.html', context)

def password_reset_request_view(request):
    """Handle password reset request"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                token = user.generate_password_reset_token()
                
                # Create password reset record
                PasswordReset.objects.create(
                    user=user,
                    token=token,
                    expires_at=timezone.now() + timezone.timedelta(hours=1)
                )
                
                # Send email (simplified - in production you'd use proper email templates)
                reset_url = request.build_absolute_uri(
                    reverse('myuser:password_reset_confirm', kwargs={'token': token})
                )
                
                send_mail(
                    'Password Reset Request',
                    f'Click the following link to reset your password: {reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                messages.success(request, 'Password reset email sent. Please check your inbox.')
                return redirect('myuser:login')
            except CustomUser.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
    else:
        form = PasswordResetRequestForm()

    context = {
        'form': form,
        'title': 'Password Reset - Ravi Pangali'
    }
    return render(request, 'myuser/password_reset_request.html', context)

def password_reset_confirm_view(request, token):
    """Handle password reset confirmation"""
    try:
        password_reset = PasswordReset.objects.get(token=token, is_used=False)
        if password_reset.is_expired():
            messages.error(request, 'Password reset link has expired.')
            return redirect('myuser:password_reset_request')
        
        if request.method == 'POST':
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():
                user = password_reset.user
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                
                # Mark token as used
                password_reset.is_used = True
                password_reset.save()
                
                messages.success(request, 'Password reset successfully! You can now login with your new password.')
                return redirect('myuser:login')
        else:
            form = PasswordResetConfirmForm()
        
        context = {
            'form': form,
            'title': 'Reset Password - Ravi Pangali'
        }
        return render(request, 'myuser/password_reset_confirm.html', context)
    except PasswordReset.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('myuser:password_reset_request')

def verify_email_view(request, token):
    """Handle email verification"""
    try:
        user = CustomUser.objects.get(email_verification_token=token)
        if user.verify_email(token):
            messages.success(request, 'Email verified successfully!')
        else:
            messages.error(request, 'Invalid or expired verification link.')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
    
    return redirect('myuser:profile')

@login_required
def resend_verification_view(request):
    """Resend email verification"""
    if request.user.is_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('myuser:profile')
    
    token = request.user.generate_email_verification_token()
    
    # Send verification email (simplified)
    verify_url = request.build_absolute_uri(
        reverse('myuser:verify_email', kwargs={'token': token})
    )
    
    send_mail(
        'Verify Your Email',
        f'Click the following link to verify your email: {verify_url}',
        settings.DEFAULT_FROM_EMAIL,
        [request.user.email],
        fail_silently=False,
    )
    
    messages.success(request, 'Verification email sent. Please check your inbox.')
    return redirect('myuser:profile')

# Firebase Views
@login_required
def firebase_apps_view(request):
    """List user's Firebase apps"""
    apps = FirebaseApp.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'apps': apps,
        'title': 'Firebase Apps - Ravi Pangali'
    }
    return render(request, 'myuser/firebase_apps.html', context)

@login_required
def firebase_app_create_view(request):
    """Create new Firebase app"""
    if request.method == 'POST':
        form = FirebaseAppForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.user = request.user
            app.save()
            messages.success(request, 'Firebase app created successfully!')
            return redirect('myuser:firebase_apps')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FirebaseAppForm()

    context = {
        'form': form,
        'title': 'Create Firebase App - Ravi Pangali'
    }
    return render(request, 'myuser/firebase_app_form.html', context)

@login_required
def firebase_app_edit_view(request, app_id):
    """Edit Firebase app"""
    app = get_object_or_404(FirebaseApp, id=app_id, user=request.user)
    
    if request.method == 'POST':
        form = FirebaseAppForm(request.POST, request.FILES, instance=app)
        if form.is_valid():
            form.save()
            messages.success(request, 'Firebase app updated successfully!')
            return redirect('myuser:firebase_apps')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FirebaseAppForm(instance=app)

    context = {
        'form': form,
        'app': app,
        'title': 'Edit Firebase App - Ravi Pangali'
    }
    return render(request, 'myuser/firebase_app_form.html', context)

@login_required
def firebase_app_delete_view(request, app_id):
    """Delete Firebase app"""
    app = get_object_or_404(FirebaseApp, id=app_id, user=request.user)
    
    if request.method == 'POST':
        app.delete()
        messages.success(request, 'Firebase app deleted successfully!')
        return redirect('myuser:firebase_apps')
    
    context = {
        'app': app,
        'title': 'Delete Firebase App - Ravi Pangali'
    }
    return render(request, 'myuser/firebase_app_confirm_delete.html', context)

@login_required
def fcm_devices_view(request, app_id):
    """List FCM devices for a Firebase app"""
    app = get_object_or_404(FirebaseApp, id=app_id, user=request.user)
    devices = FcmDevice.objects.filter(firebase_app=app).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(devices, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'app': app,
        'devices': page_obj,
        'total_devices': devices.count(),
        'active_devices': devices.filter(is_active=True).count(),
        'notifications_sent': PushNotification.objects.filter(firebase_app=app).count(),
        'title': f'FCM Devices - {app.name}'
    }
    return render(request, 'myuser/fcm_devices.html', context)

@login_required
def fcm_device_add_view(request, app_id):
    """Add FCM device"""
    app = get_object_or_404(FirebaseApp, id=app_id, user=request.user)
    
    if request.method == 'POST':
        form = FcmDeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.firebase_app = app
            device.save()
            messages.success(request, 'Device added successfully!')
            return redirect('myuser:fcm_devices', app_id=app_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FcmDeviceForm()

    context = {
        'form': form,
        'app': app,
        'title': f'Add Device - {app.name}'
    }
    return render(request, 'myuser/fcm_device_form.html', context)

@login_required
def send_notification_view(request, app_id):
    """Send push notification"""
    app = get_object_or_404(FirebaseApp, id=app_id, user=request.user)
    
    if request.method == 'POST':
        form = PushNotificationForm(request.POST)
        if form.is_valid():
            # Get Firebase service
            service = get_firebase_service(app_id)
            if not service:
                messages.error(request, 'Firebase service not available.')
                return redirect('myuser:firebase_apps')
            
            # Prepare notification data
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            image_url = form.cleaned_data.get('image_url')
            data = form.cleaned_data.get('data', {})
            priority = form.cleaned_data['priority']
            notification_type = form.cleaned_data.get('notification_type', '')
            sound = form.cleaned_data.get('sound', '')
            data_only = form.cleaned_data.get('data_only', False)
            is_alarm = form.cleaned_data.get('is_alarm', False)
            urgent = form.cleaned_data.get('urgent', False)
            persistent = form.cleaned_data.get('persistent', False)
            
            # Handle data field (convert string to dict if needed)
            if isinstance(data, str) and data:
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    messages.error(request, 'Invalid JSON in custom data field.')
                    context = {'form': form, 'app': app, 'title': f'Send Notification - {app.name}'}
                    return render(request, 'myuser/send_notification.html', context)
            
            # Determine tokens to send to
            send_to_all = form.cleaned_data.get('send_to_all', True)
            token_input = form.cleaned_data.get('token_input', '')
            
            # Debug: Check if there are any devices
            device_count = app.devices.filter(is_active=True).count()
            print(f"DEBUG: Found {device_count} active devices for app {app.name}")
            
            if send_to_all:
                # Send to all devices
                result = service.send_to_all_devices(
                    title=title,
                    body=body,
                    image_url=image_url,
                    data=data,
                    priority=priority,
                    notification_type=notification_type,
                    sound=sound,
                    data_only=data_only,
                    is_alarm=is_alarm,
                    urgent=urgent,
                    persistent=persistent
                )
            else:
                # Send to specific tokens
                tokens = [token.strip() for token in token_input.split('\n') if token.strip()]
                if not tokens:
                    messages.error(request, 'Please provide at least one token.')
                    context = {'form': form, 'app': app, 'title': f'Send Notification - {app.name}'}
                    return render(request, 'myuser/send_notification.html', context)
                
                result = service.send_to_specific_tokens(
                    title=title,
                    body=body,
                    tokens=tokens,
                    image_url=image_url,
                    data=data,
                    priority=priority,
                    notification_type=notification_type,
                    sound=sound,
                    data_only=data_only,
                    is_alarm=is_alarm,
                    urgent=urgent,
                    persistent=persistent
                )
            
            # Debug: Print result
            print(f"DEBUG: Notification result: {result}")
            
            if result['success']:
                messages.success(
                    request, 
                    f'Notification sent successfully! Delivered: {result["tokens_delivered"]}, Failed: {result["tokens_failed"]}'
                )
                return redirect('myuser:firebase_apps')
            else:
                messages.error(request, f'Failed to send notification: {result["error"]}')
        else:
            # Debug: Print form errors
            print(f"DEBUG: Form errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PushNotificationForm()

    context = {
        'form': form,
        'app': app,
        'title': f'Send Notification - {app.name}'
    }
    return render(request, 'myuser/send_notification.html', context)

@login_required
def test_firebase_connection_view(request, app_id):
    """Test Firebase app connection"""
    app = get_object_or_404(FirebaseApp, id=app_id, user=request.user)
    
    result = test_firebase_app(app_id)
    
    if result['success']:
        messages.success(request, f'Connection test successful: {result["message"]}')
    else:
        messages.error(request, f'Connection test failed: {result["message"]}')
    
    return redirect('myuser:firebase_apps')

# API endpoints for AJAX requests
@csrf_exempt
@require_http_methods(["POST"])
def ajax_login(request):
    """AJAX login endpoint"""
    if request.user.is_authenticated:
        return JsonResponse({'success': True, 'redirect': reverse('home')})

    form = CustomAuthenticationForm(request, data=request.POST)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = authenticate(username=username, password=password)
        if user is None:
            try:
                user_obj = CustomUser.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass

        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': f'Welcome back, {user.display_name}!',
                'redirect': request.GET.get('next', reverse('home'))
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid username/email or password.'
            })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Please correct the errors below.',
            'errors': form.errors
        })

# Firebase API endpoints
@csrf_exempt
@require_http_methods(["POST"])
def ajax_add_device(request, app_id):
    """AJAX endpoint to add FCM device"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'})
    
    try:
        app = FirebaseApp.objects.get(id=app_id, user=request.user)
    except FirebaseApp.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Firebase app not found'})
    
    try:
        data = json.loads(request.body)
        token = data.get('token')
        device_id = data.get('device_id', '')
        device_type = data.get('device_type', 'unknown')
        
        if not token:
            return JsonResponse({'success': False, 'error': 'Token is required'})
        
        # Check if device already exists
        device, created = FcmDevice.objects.get_or_create(
            firebase_app=app,
            token=token,
            defaults={
                'device_id': device_id,
                'device_type': device_type
            }
        )
        
        if not created:
            # Update existing device
            device.device_id = device_id
            device.device_type = device_type
            device.is_active = True
            device.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Device registered successfully',
            'device_id': str(device.id)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def ajax_send_notification(request, app_id):
    """AJAX endpoint to send notification"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'})
    
    try:
        app = FirebaseApp.objects.get(id=app_id, user=request.user)
    except FirebaseApp.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Firebase app not found'})
    
    try:
        data = json.loads(request.body)
        title = data.get('title')
        body = data.get('body')
        tokens = data.get('tokens', [])
        image_url = data.get('image_url')
        custom_data = data.get('data', {})
        priority = data.get('priority', 'high')
        
        # Parse additional notification parameters
        notification_type = data.get('type', '')
        sound = data.get('sound', '')
        data_only = data.get('data_only', False)
        is_alarm = data.get('is_alarm', False)
        urgent = data.get('urgent', False)
        persistent = data.get('persistent', False)
        
        if not title or not body:
            return JsonResponse({'success': False, 'error': 'Title and body are required'})
        
        # Get Firebase service
        service = get_firebase_service(app_id)
        if not service:
            return JsonResponse({'success': False, 'error': 'Firebase service not available'})
        
        # Send notification
        if tokens:
            result = service.send_to_specific_tokens(
                title=title,
                body=body,
                tokens=tokens,
                image_url=image_url,
                data=custom_data,
                priority=priority,
                notification_type=notification_type,
                sound=sound,
                data_only=data_only,
                is_alarm=is_alarm,
                urgent=urgent,
                persistent=persistent
            )
        else:
            result = service.send_to_all_devices(
                title=title,
                body=body,
                image_url=image_url,
                data=custom_data,
                priority=priority,
                notification_type=notification_type,
                sound=sound,
                data_only=data_only,
                is_alarm=is_alarm,
                urgent=urgent,
                persistent=persistent
            )
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["GET"])
def ajax_get_devices(request):
    """AJAX endpoint to get user's devices"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'})
    
    try:
        devices = FcmDevice.objects.filter(
            firebase_app__user=request.user,
            is_active=True
        ).select_related('firebase_app')
        
        device_list = []
        for device in devices:
            device_list.append({
                'id': str(device.id),
                'app_name': device.firebase_app.name,
                'device_type': device.device_type,
                'device_id': device.device_id or '',
                'token_preview': device.token[:50] + '...' if len(device.token) > 50 else device.token,
                'last_used': device.last_used.strftime('%Y-%m-%d %H:%M:%S') if device.last_used else 'Never'
            })
        
        return JsonResponse({
            'success': True,
            'devices': device_list
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def ajax_quick_notification(request):
    """AJAX endpoint for quick notification sending"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'})
    
    try:
        data = json.loads(request.body)
        title = data.get('title')
        body = data.get('body')
        
        if not title or not body:
            return JsonResponse({'success': False, 'error': 'Title and body are required'})
        
        # Get user's first active Firebase app
        app = FirebaseApp.objects.filter(user=request.user, is_active=True).first()
        if not app:
            return JsonResponse({'success': False, 'error': 'No active Firebase app found'})
        
        # Get Firebase service
        service = get_firebase_service(str(app.id))
        if not service:
            return JsonResponse({'success': False, 'error': 'Firebase service not available'})
        
        # Parse additional notification parameters
        notification_type = data.get('type', '')
        sound = data.get('sound', '')
        data_only = data.get('data_only', False)
        is_alarm = data.get('is_alarm', False)
        urgent = data.get('urgent', False)
        persistent = data.get('persistent', False)
        
        # Send to all devices
        result = service.send_to_all_devices(
            title=title, 
            body=body,
            notification_type=notification_type,
            sound=sound,
            data_only=data_only,
            is_alarm=is_alarm,
            urgent=urgent,
            persistent=persistent
        )
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': f'Notification sent! Delivered: {result["tokens_delivered"]}, Failed: {result["tokens_failed"]}'
            })
        else:
            return JsonResponse({'success': False, 'error': result['error']})
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def api_documentation_view(request):
    """API documentation page"""
    return render(request, 'myuser/api_documentation.html', {
        'title': 'API Documentation'
    })

# Django REST Framework API Views (Function-based with email/password auth)
@api_view(['POST'])
@permission_classes([AllowAny])
def firebase_notification_api(request, app_id):
    """DRF API endpoint for sending Firebase push notifications"""
    try:
        # Extract authentication credentials
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'success': False,
                'error': 'Email and password are required for authentication'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(username=email, password=password)
        if user is None:
            # Try with email field
            try:
                user_obj = CustomUser.objects.get(email=email)
                user = authenticate(username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass
        
        if user is None:
            return Response({
                'success': False,
                'error': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'success': False,
                'error': 'Account is disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get Firebase app
        try:
            app = FirebaseApp.objects.get(id=app_id, user=user)
        except FirebaseApp.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Firebase app not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Parse notification data
        title = request.data.get('title')
        body = request.data.get('body')
        tokens = request.data.get('tokens', [])
        image_url = request.data.get('image_url')
        custom_data = request.data.get('data', {})
        priority = request.data.get('priority', 'high')
        
        # Parse additional notification parameters
        notification_type = request.data.get('type', '')
        sound = request.data.get('sound', '')
        data_only = request.data.get('data_only', False)
        is_alarm = request.data.get('is_alarm', False)
        urgent = request.data.get('urgent', False)
        persistent = request.data.get('persistent', False)
        
        # Validate required fields
        if not title or not body:
            return Response({
                'success': False,
                'error': 'Title and body are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate priority
        if priority not in ['normal', 'high', 'urgent']:
            return Response({
                'success': False,
                'error': 'Priority must be normal, high, or urgent'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get Firebase service
        service = get_firebase_service(str(app_id))
        if not service:
            return Response({
                'success': False,
                'error': 'Firebase service not available'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Send notification
        if tokens:
            result = service.send_to_specific_tokens(
                title=title,
                body=body,
                tokens=tokens,
                image_url=image_url,
                data=custom_data,
                priority=priority,
                notification_type=notification_type,
                sound=sound,
                data_only=data_only,
                is_alarm=is_alarm,
                urgent=urgent,
                persistent=persistent
            )
        else:
            result = service.send_to_all_devices(
                title=title,
                body=body,
                image_url=image_url,
                data=custom_data,
                priority=priority,
                notification_type=notification_type,
                sound=sound,
                data_only=data_only,
                is_alarm=is_alarm,
                urgent=urgent,
                persistent=persistent
            )
        
        # Return appropriate response
        if result.get('success'):
            return Response({
                'success': True,
                'message': 'Notification sent successfully',
                'notification_id': result.get('notification_id'),
                'tokens_sent': result.get('tokens_sent', 0),
                'tokens_delivered': result.get('tokens_delivered', 0),
                'tokens_failed': result.get('tokens_failed', 0),
                'details': result.get('results', {})
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Failed to send notification')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def firebase_device_add_api(request, app_id):
    """DRF API endpoint for adding/updating FCM devices"""
    try:
        # Extract authentication credentials
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'success': False,
                'error': 'Email and password are required for authentication'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(username=email, password=password)
        if user is None:
            # Try with email field
            try:
                user_obj = CustomUser.objects.get(email=email)
                user = authenticate(username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass
        
        if user is None:
            return Response({
                'success': False,
                'error': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'success': False,
                'error': 'Account is disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get Firebase app
        try:
            app = FirebaseApp.objects.get(id=app_id, user=user)
        except FirebaseApp.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Firebase app not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Parse device data
        token = request.data.get('token')
        device_id = request.data.get('device_id', '')
        device_type = request.data.get('device_type', 'unknown')
        
        # Validate required fields
        if not token:
            return Response({
                'success': False,
                'error': 'Token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate device type
        valid_device_types = ['android', 'web', 'unknown']
        if device_type not in valid_device_types:
            return Response({
                'success': False,
                'error': f'Device type must be one of: {", ".join(valid_device_types)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if device already exists
        device, created = FcmDevice.objects.get_or_create(
            firebase_app=app,
            token=token,
            defaults={
                'device_id': device_id,
                'device_type': device_type
            }
        )
        
        if not created:
            # Update existing device
            device.device_id = device_id
            device.device_type = device_type
            device.is_active = True
            device.save()
        
        return Response({
            'success': True,
            'message': 'Device registered successfully',
            'device_id': str(device.id),
            'created': created,
            'device_type': device.device_type
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def firebase_devices_list_api(request, app_id):
    """DRF API endpoint for listing FCM devices"""
    try:
        # Extract authentication credentials from query params or headers
        email = request.GET.get('email') or request.headers.get('X-Email')
        password = request.GET.get('password') or request.headers.get('X-Password')
        
        if not email or not password:
            return Response({
                'success': False,
                'error': 'Email and password are required for authentication'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(username=email, password=password)
        if user is None:
            # Try with email field
            try:
                user_obj = CustomUser.objects.get(email=email)
                user = authenticate(username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass
        
        if user is None:
            return Response({
                'success': False,
                'error': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'success': False,
                'error': 'Account is disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get Firebase app
        try:
            app = FirebaseApp.objects.get(id=app_id, user=user)
        except FirebaseApp.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Firebase app not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get devices
        devices = FcmDevice.objects.filter(
            firebase_app=app,
            is_active=True
        ).order_by('-created_at')
        
        device_list = []
        for device in devices:
            device_list.append({
                'id': str(device.id),
                'device_type': device.device_type,
                'device_id': device.device_id or '',
                'token_preview': device.token[:50] + '...' if len(device.token) > 50 else device.token,
                'last_used': device.last_used.strftime('%Y-%m-%d %H:%M:%S') if device.last_used else 'Never',
                'created_at': device.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return Response({
            'success': True,
            'devices': device_list,
            'total_devices': len(device_list)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)