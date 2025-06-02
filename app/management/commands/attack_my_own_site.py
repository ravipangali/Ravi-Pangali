from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, date
from decimal import Decimal
import requests
import json
from app.models import *

class Command(BaseCommand):
    help = 'Attacking those site which is made my myself'

    def handle(self, *args, **options):
        self.stdout.write('Attacking those site which is made my myself')
        self.stdout.write(self.style.SUCCESS('Starting attacking...'))

        # Ask for site URL
        site_url = input("Enter the site URL (e.g., https://example.com): ").strip()
        
        # Remove trailing slash if present
        if site_url.endswith('/'):
            site_url = site_url[:-1]
        
        # Create the target URL
        target_url = f"{site_url}/change-site-status"
        self.stdout.write(f"Target URL: {target_url}")
        
        # Ask for site status
        while True:
            status_input = input("Enter site status (True/False): ").strip().lower()
            if status_input in ['true', 'false']:
                status = status_input == 'true'
                break
            else:
                self.stdout.write(self.style.ERROR("Please enter 'True' or 'False'"))
        
        # Prepare POST data
        post_data = {
            'status': status
        }
        
        # If status is False, ask for description
        if not status:
            description = input("Enter description: ").strip()
            post_data['description'] = description
        else:
            # If status is True, we can still include an empty description or skip it
            post_data['description'] = ""
        
        # Display the data that will be sent
        self.stdout.write(f"POST data: {json.dumps(post_data, indent=2)}")
        
        try:
            # Make the POST request
            response = requests.post(target_url, json=post_data, timeout=30)
            
            # Display response information
            self.stdout.write(f"Response Status Code: {response.status_code}")
            self.stdout.write(f"Response Headers: {dict(response.headers)}")
            
            try:
                response_json = response.json()
                self.stdout.write(f"Response JSON: {json.dumps(response_json, indent=2)}")
            except:
                self.stdout.write(f"Response Text: {response.text}")
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('Request sent successfully!'))
            else:
                self.stdout.write(self.style.WARNING(f'Request completed with status code: {response.status_code}'))
                
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Request failed: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Attacking completed successfully!'))