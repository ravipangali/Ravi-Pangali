from django.urls import path
from . import views

app_name = 'myuser'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    # path('register/', views.register_view, name='register'),  # Registration disabled
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('ajax-login/', views.ajax_login, name='ajax_login'),
    
    # Password management
    path('password/change/', views.password_change_view, name='password_change'),
    path('password/reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password/reset/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    
    # Email verification
    path('verify-email/<str:token>/', views.verify_email_view, name='verify_email'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),
    
    # Firebase Apps
    path('firebase/apps/', views.firebase_apps_view, name='firebase_apps'),
    path('firebase/apps/create/', views.firebase_app_create_view, name='firebase_app_create'),
    path('firebase/apps/<uuid:app_id>/edit/', views.firebase_app_edit_view, name='firebase_app_edit'),
    path('firebase/apps/<uuid:app_id>/delete/', views.firebase_app_delete_view, name='firebase_app_delete'),
    path('firebase/apps/<uuid:app_id>/test/', views.test_firebase_connection_view, name='test_firebase_connection'),
    
    # FCM Devices
    path('firebase/apps/<uuid:app_id>/devices/', views.fcm_devices_view, name='fcm_devices'),
    path('firebase/apps/<uuid:app_id>/devices/add/', views.fcm_device_add_view, name='fcm_device_add'),
    
    # Push Notifications
    path('firebase/apps/<uuid:app_id>/send/', views.send_notification_view, name='send_notification'),
    
    # Firebase API endpoints (DRF with email/password auth)
    path('api/firebase/apps/<uuid:app_id>/notifications/', views.firebase_notification_api, name='firebase_notification_api'),
    path('api/firebase/apps/<uuid:app_id>/devices/', views.firebase_device_add_api, name='firebase_device_add_api'),
    path('api/firebase/apps/<uuid:app_id>/devices/list/', views.firebase_devices_list_api, name='firebase_devices_list_api'),
    
    # Legacy AJAX endpoints (keeping for backward compatibility)
    path('api/firebase/apps/<uuid:app_id>/devices/legacy/', views.ajax_add_device, name='ajax_add_device'),
    path('api/firebase/apps/<uuid:app_id>/notifications/legacy/', views.ajax_send_notification, name='ajax_send_notification'),
    path('api/firebase/devices/legacy/', views.ajax_get_devices, name='ajax_get_devices'),
    path('api/firebase/quick-notification/legacy/', views.ajax_quick_notification, name='ajax_quick_notification'),
    
    # API Documentation
    path('api-docs/', views.api_documentation_view, name='api_documentation'),
]