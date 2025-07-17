import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests
import tempfile
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.conf import settings
from .models import FirebaseApp, FcmDevice, PushNotification

class FirebaseService:
    """Firebase service for sending push notifications using FCM API"""
    
    def __init__(self, firebase_app):
        """
        Initialize Firebase service with a FirebaseApp instance
        
        Args:
            firebase_app: FirebaseApp model instance
        """
        self.firebase_app = firebase_app
        self.project_id = firebase_app.project_id
        self.service_account_path = firebase_app.get_service_account_path()
        self.session = self._create_session_with_retry()
    
    def _create_session_with_retry(self):
        """Create a requests session with retry logic"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_access_token(self):
        """Extract access token from service account JSON file"""
        try:
            if not self.service_account_path or not os.path.exists(self.service_account_path):
                raise Exception("Service account file not found")
            
            # Create credentials from service account file
            SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_path, scopes=SCOPES)

            # Get access token
            auth_req = google.auth.transport.requests.Request()
            credentials.refresh(auth_req)
            access_token = credentials.token
            
            return access_token
            
        except Exception as e:
            raise Exception(f"Failed to extract access token: {str(e)}")
    
    def test_connection(self):
        """Test FCM API connection using access token"""
        try:
            # Extract access token
            access_token = self._get_access_token()
            
            # Test FCM endpoint
            url = f'https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send'
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json; UTF-8',
            }
            
            # Send a test request
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return True, "FCM API connection successful"
            else:
                return False, f"FCM API connection failed: {response.status_code}"
                
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def send_notification(self, title, body, tokens=None, image_url=None, data=None, priority='high'):
        """
        Send push notification using FCM API
        
        Args:
            title: Notification title
            body: Notification body
            tokens: List of FCM tokens (if None, sends to all devices)
            image_url: Optional image URL
            data: Optional custom data
            priority: 'normal' or 'high'
        
        Returns:
            dict: Result with success status and details
        """
        try:
            # Extract access token from service account
            access_token = self._get_access_token()
            
            # Get tokens to send to
            if tokens is None:
                # Get all active devices for this app
                devices = FcmDevice.objects.filter(
                    firebase_app=self.firebase_app,
                    is_active=True
                )
                tokens = [device.token for device in devices]
            
            if not tokens:
                return {
                    'success': False,
                    'error': 'No tokens to send to'
                }
            
            # FCM API endpoint
            url = f'https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send'
            
            # Prepare notification data
            notification_data = {
                "title": title,
                "body": body
            }
            
            if image_url:
                notification_data["image"] = image_url
            
            # Prepare message data
            message_data = data or {}
            message_data["timestamp"] = str(int(time.time()))
            
            # Send to each token
            results = []
            successful = 0
            failed = 0
            
            for token in tokens:
                try:
                    # Prepare FCM message payload
                    message = {
                        "message": {
                            "token": token,
                            "notification": notification_data,
                            "data": message_data,
                            "android": {
                                "priority": priority
                            },
                            "apns": {
                                "headers": {
                                    "apns-priority": "10" if priority == 'high' else "5"
                                }
                            }
                        }
                    }
                    
                    # Send FCM API request
                    headers = {
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json; UTF-8',
                    }
                    
                    response = self.session.post(url, headers=headers, json=message, timeout=30)
                    
                    if response.status_code == 200:
                        successful += 1
                        results.append({
                            'token': token,
                            'success': True,
                            'response': response.json()
                        })
                    else:
                        failed += 1
                        results.append({
                            'token': token,
                            'success': False,
                            'error': f"HTTP {response.status_code}",
                            'response': response.text
                        })
                        
                except Exception as e:
                    failed += 1
                    results.append({
                        'token': token,
                        'success': False,
                        'error': str(e)
                    })
            
            # Create notification record
            notification = PushNotification.objects.create(
                firebase_app=self.firebase_app,
                title=title,
                body=body,
                image_url=image_url,
                data=data or {},
                priority=priority,
                tokens_sent=len(tokens),
                tokens_delivered=successful,
                tokens_failed=failed
            )
            
            return {
                'success': True,
                'notification_id': str(notification.id),
                'tokens_sent': len(tokens),
                'tokens_delivered': successful,
                'tokens_failed': failed,
                'results': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_to_specific_tokens(self, title, body, tokens, image_url=None, data=None, priority='high'):
        """Send notification to specific tokens using FCM API"""
        return self.send_notification(
            title=title,
            body=body,
            tokens=tokens,
            image_url=image_url,
            data=data,
            priority=priority
        )
    
    def send_to_all_devices(self, title, body, image_url=None, data=None, priority='high'):
        """Send notification to all devices for this app using FCM API"""
        return self.send_notification(
            title=title,
            body=body,
            tokens=None,  # This will get all devices
            image_url=image_url,
            data=data,
            priority=priority
        )

def get_firebase_service(firebase_app_id):
    """
    Get Firebase service for a specific app
    
    Args:
        firebase_app_id: UUID of FirebaseApp
    
    Returns:
        FirebaseService instance or None if app not found
    """
    try:
        firebase_app = FirebaseApp.objects.get(id=firebase_app_id)
        return FirebaseService(firebase_app)
    except FirebaseApp.DoesNotExist:
        return None

def test_firebase_app(firebase_app_id):
    """
    Test FCM API connection for a Firebase app
    
    Args:
        firebase_app_id: UUID of FirebaseApp
    
    Returns:
        dict: Test results
    """
    service = get_firebase_service(firebase_app_id)
    if not service:
        return {
            'success': False,
            'error': 'Firebase app not found'
        }
    
    success, message = service.test_connection()
    return {
        'success': success,
        'message': message
    } 