from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from .models import Project
from datetime import datetime, timedelta

class StaticViewSitemap(Sitemap):
    """Sitemap for static views/pages"""
    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'  # Use https for better security

    def items(self):
        # Return the names of all static views you want in the sitemap
        return ['home']

    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        # Return the last modified date of the view
        return datetime.now()

class ProjectSitemap(Sitemap):
    """Sitemap for Project model items"""
    changefreq = 'monthly'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return Project.objects.all()

    def location(self, obj):
        # Use the get_absolute_url method from the model
        return obj.get_absolute_url()
    
    def lastmod(self, obj):
        # If your model has a last_modified field, you would use it here
        # For now, using a mock date (you may want to add this field to your model)
        return datetime.now() - timedelta(days=30)  # Assume updated a month ago 