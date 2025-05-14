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