from .models import Profile

def profile_context(request):
    """
    Context processor that adds the profile object to all templates
    """
    try:
        profile = Profile.objects.first()
    except:
        profile = None
    
    return {
        'profile': profile
    }

def site_context(request):
    """Add site-wide context variables"""
    return {
        'is_secure': request.is_secure(),
        'site_domain': request.get_host(),
        'site_url': request.build_absolute_uri('/').rstrip('/'),
    } 