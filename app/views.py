from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
import requests
from django.contrib.auth.decorators import login_required
import json
from .models import Profile, About, Project, TechnicalSkill, SoftSkill, Experience

# Create your views here.
def home(request):
    # Handle form submission
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Form validation
        if name and email and subject and message:
            # Get admin email from profile or use a default
            try:
                profile = Profile.objects.first()
                admin_email = profile.email if profile else settings.DEFAULT_FROM_EMAIL
            except:
                admin_email = settings.DEFAULT_FROM_EMAIL
            
            # Compose email message
            email_message = f"Name: {name}\nEmail: {email}\n\n{message}"
            
            # Send email
            try:
                send_mail(
                    subject=f"Portfolio Contact: {subject}",
                    message=email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin_email],
                    fail_silently=False,
                )
                messages.success(request, "Your message has been sent. Thank you!")
            except Exception as e:
                messages.error(request, f"There was an error sending your message. Please try again later.")
        else:
            messages.error(request, "Please fill in all fields.")
        
        return redirect('home')  # Redirect to avoid form resubmission
    
    # Get singleton models (should only have one instance)
    try:
        profile = Profile.objects.first()
    except Profile.DoesNotExist:
        profile = None
        
    try:
        about = About.objects.first()
    except About.DoesNotExist:
        about = None
    
    # Get collections
    projects = Project.objects.all()
    technical_skills = TechnicalSkill.objects.all()
    soft_skills = SoftSkill.objects.all()
    experiences = Experience.objects.all()
    
    # SEO Context
    meta_description = profile.meta_description if profile and profile.meta_description else f"Professional Portfolio of {profile.name if profile else 'Ravi Pangali'} - {profile.title if profile else 'Full Stack Developer'}"
    meta_keywords = profile.meta_keywords if profile and profile.meta_keywords else "developer, portfolio, web development, full stack"
    
    context = {
        'profile': profile,
        'about': about,
        'projects': projects,
        'technical_skills': technical_skills,
        'soft_skills': soft_skills,
        'experiences': experiences,
        'meta_description': meta_description,
        'meta_keywords': meta_keywords,
        'canonical_url': request.build_absolute_uri(),
    }
    
    return render(request, 'home.html', context)

def project_detail(request, project_id):
    """Display details for a specific project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Get profile for context
    try:
        profile = Profile.objects.first()
    except Profile.DoesNotExist:
        profile = None
    
    # Get canonical URL for this project
    canonical_url = request.build_absolute_uri()
    
    # SEO metadata
    meta_title = project.meta_title if project.meta_title else f"{project.title} | {profile.name if profile else 'Ravi Pangali'} Portfolio"
    meta_description = project.meta_description if project.meta_description else project.description[:157] + "..."
    meta_keywords = project.meta_keywords if project.meta_keywords else f"developer, portfolio, project, {profile.name if profile else 'Ravi Pangali'}, {project.title}"
    
    context = {
        'project': project,
        'profile': profile,
        'canonical_url': canonical_url,
        'meta_title': meta_title,
        'meta_description': meta_description,
        'meta_keywords': meta_keywords,
    }
    
    return render(request, 'project_detail.html', context)


@login_required(login_url='home')
def attack_my_sites(request):
    """Handle site attacking functionality"""
    context = {
        'result': None,
        'error': None,
        'form_data': {},
    }
    
    if request.method == 'POST':
        # Get form data
        site_url = request.POST.get('site_url', '').strip()
        status = request.POST.get('status', '').lower()
        description = request.POST.get('description', '').strip()
        
        # Store form data to repopulate form on error
        context['form_data'] = {
            'code': 'livi',
            'site_url': site_url,
            'status': status,
            'description': description,
        }
        
        # Validate inputs
        if not site_url:
            context['error'] = "Please enter a site URL"
            return render(request, 'app/attack_my_sites.html', context)
        
        if status not in ['true', 'false']:
            context['error'] = "Please select a valid status (True or False)"
            return render(request, 'app/attack_my_sites.html', context)
        
        # Convert status to boolean
        status_bool = status == 'true'
        
        # If status is False, description is required
        if not status_bool and not description:
            context['error'] = "Description is required when status is False"
            return render(request, 'app/attack_my_sites.html', context)
        
        # Clean up URL
        if site_url.endswith('/'):
            site_url = site_url[:-1]
        
        # Create target URL
        target_url = f"{site_url}/change-site-status"
        
        # Prepare POST data
        post_data = {
            'status': status_bool,
            'description': description if not status_bool else ""
        }
        
        try:
            # Make the POST request
            response = requests.post(target_url, json=post_data, timeout=30)
            
            # Prepare result data
            result_data = {
                'target_url': target_url,
                'post_data': post_data,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'success': response.status_code == 200,
            }
            
            # Try to parse JSON response
            try:
                result_data['response_json'] = response.json()
                result_data['response_text'] = None
            except:
                result_data['response_json'] = None
                result_data['response_text'] = response.text
            
            context['result'] = result_data
            
            if response.status_code == 200:
                messages.success(request, "Request sent successfully!")
            else:
                messages.warning(request, f"Request completed with status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            context['error'] = f"Request failed: {str(e)}"
        except Exception as e:
            context['error'] = f"An error occurred: {str(e)}"
    
    return render(request, 'app/attack_my_sites.html', context)

