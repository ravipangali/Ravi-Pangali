import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests
import tempfile
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Firebase service account URL
SERVICE_ACCOUNT_URL = 'http://127.0.0.1:8000/media/firebase_services/luna-iot-5993f-firebase-adminsdk-fbsvc-9980e81d5a.json'

# Target device token
DEVICE_TOKEN = 'cSMQwCvFT8yZEP_mpqPsu_:APA91bFDpU_GXdsXXxamS8TpGjCybOEXqDzLyEo38z8W7nEfrgvspbe4RU8hAJZ5T7t7ectX76SaIbAxtcKpvSUk1_NwRSZFAzdN1T_UHo-jnw7vnHAW89o'

def create_session_with_retry():
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

def download_service_account_file():
    """Download service account file from URL"""
    try:
        print("Downloading Firebase service account file...")
        session = create_session_with_retry()
        response = session.get(SERVICE_ACCOUNT_URL, timeout=30)
        
        if response.status_code == 200:
            # Parse the JSON to get project ID
            service_data = response.json()
            project_id = service_data.get('project_id')
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(service_data, f)
                temp_file_path = f.name
            
            print(f"✓ Service account file downloaded successfully")
            print(f"✓ Project ID: {project_id}")
            return temp_file_path, project_id
        else:
            print(f"✗ Failed to download service account file. Status code: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"✗ Error downloading service account file: {e}")
        return None, None

def send_push_notification(service_account_file, project_id):
    """Send push notification using FCM API"""
    try:
        print(f"\nSending push notification to project: {project_id}")
        
        # Create a scoped credentials object
        SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file, scopes=SCOPES)

        # Get an access token
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        access_token = credentials.token
        
        print("✓ Access token obtained successfully")

        # FCM endpoint for sending messages
        url = f'https://fcm.googleapis.com/v1/projects/{project_id}/messages:send'

        # Message payload
        message = {
            "message": {
                "token": DEVICE_TOKEN,
                "notification": {
                    "title": "Hello from Python FCM",
                    "body": "This is a push notification sent via FCM API using downloaded service account"
                },
                "data": {
                    "custom_key": "custom_value",
                    "timestamp": str(int(time.time()))
                }
            }
        }

        # Send the POST request with retry logic
        session = create_session_with_retry()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; UTF-8',
        }

        print("Sending notification...")
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Message: {json.dumps(message, indent=2)}")
        
        response = session.post(url, headers=headers, json=message, timeout=30)

        # Show the result
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response Body: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✓ Push notification sent successfully!")
        else:
            print("✗ Failed to send push notification")
            
    except requests.exceptions.ConnectionError as e:
        print(f"✗ Connection error: {e}")
        print("This might be due to:")
        print("- Network connectivity issues")
        print("- Firewall blocking the connection")
        print("- FCM service temporarily unavailable")
        print("- Invalid project ID or credentials")
        
    except requests.exceptions.Timeout as e:
        print(f"✗ Timeout error: {e}")
        print("The request timed out. Try again later.")
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Request error: {e}")
        
    except Exception as e:
        print(f"✗ Error sending push notification: {e}")
        print(f"Error type: {type(e).__name__}")

def test_network_connectivity():
    """Test basic network connectivity"""
    print("Testing network connectivity...")
    
    try:
        # Test basic internet connectivity
        response = requests.get("https://www.google.com", timeout=10)
        print("✓ Basic internet connectivity: OK")
        
        # Test FCM endpoint accessibility
        response = requests.get("https://fcm.googleapis.com", timeout=10)
        print("✓ FCM endpoint accessible: OK")
        
        return True
    except Exception as e:
        print(f"✗ Network connectivity issue: {e}")
        return False

def main():
    """Main function to test Firebase push notification"""
    print("=== Firebase Push Notification Test ===")
    print(f"Device Token: {DEVICE_TOKEN[:50]}...")
    
    # Test network connectivity first
    if not test_network_connectivity():
        print("✗ Cannot proceed due to network issues")
        return
    
    # Download service account file
    service_account_file, project_id = download_service_account_file()
    
    if service_account_file and project_id:
        # Send push notification
        send_push_notification(service_account_file, project_id)
        
        # Clean up temporary file
        try:
            os.unlink(service_account_file)
            print("✓ Temporary file cleaned up")
        except:
            pass
    else:
        print("✗ Cannot proceed without service account file")

if __name__ == "__main__":
    main()
