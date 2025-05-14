from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Profile, About, Project, TechnicalSkill, SoftSkill, Experience
from django.views.decorators.cache import cache_page
from django.views.decorators.http import condition

# Create ETags for caching based on model updates
def get_latest_update_time():
    # Get latest update from models
    last_profile_update = Profile.objects.latest('id').id if Profile.objects.exists() else 0
    last_about_update = About.objects.latest('id').id if About.objects.exists() else 0
    last_project_update = Project.objects.latest('id').id if Project.objects.exists() else 0
    
    # Return the latest update ID
    return max(last_profile_update, last_about_update, last_project_update)

# Cache home page for 5 minutes (300 seconds)
@cache_page(300)
@condition(last_modified_func=get_latest_update_time)
def home(request):
    # Skip cache for POST requests
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
    
    context = {
        'profile': profile,
        'about': about,
        'projects': projects,
        'technical_skills': technical_skills,
        'soft_skills': soft_skills,
        'experiences': experiences,
    }
    
    return render(request, 'home.html', context)

