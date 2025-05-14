from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import requests
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
        recaptcha_response = request.POST.get('g-recaptcha-response')
        
        # Check if reCAPTCHA is valid
        recaptcha_valid = verify_recaptcha(recaptcha_response)
        
        # Form validation
        if name and email and subject and message and recaptcha_valid:
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
        elif not recaptcha_valid:
            messages.error(request, "reCAPTCHA verification failed. Please try again.")
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

def verify_recaptcha(response):
    """
    Verify the reCAPTCHA response with Google
    """
    if not response:
        return False
        
    try:
        data = {
            'secret': '6LebYTorAAAAAFmO_qp9PyJpcVhDdDZ4pa8Ly11k',  # Replace with your actual secret key
            'response': response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = json.loads(r.text)
        return result.get('success', False)
    except:
        return False

