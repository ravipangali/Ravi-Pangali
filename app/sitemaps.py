from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from .models import Project

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

class ProjectSitemap(Sitemap):
    """Sitemap for Project model items"""
    changefreq = 'monthly'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return Project.objects.all()

    def location(self, obj):
        # Since you don't have a dedicated project detail page, return the home URL with an anchor
        return f"{reverse('home')}#project-{obj.id}" 