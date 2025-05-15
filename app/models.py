from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils import timezone
from .utils import optimize_image

class Profile(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=150, help_text="Your professional title or role")
    avatar = models.ImageField(upload_to='profile/', blank=True, null=True)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=30, blank=True, null=True, help_text="Phone number (e.g. +1 234 567 8900)")
    location = models.CharField(max_length=100)
    
    # SEO fields
    meta_description = models.CharField(max_length=160, blank=True, null=True, 
                                      help_text="Description for search engines (max 160 characters)")
    meta_keywords = models.CharField(max_length=200, blank=True, null=True,
                                   help_text="Keywords for search engines (comma separated)")
    
    # Social links
    github = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    
    # Timestamps for SEO
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profile"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Optimize avatar image if provided
        if self.avatar:
            self.avatar = optimize_image(self.avatar)
        super().save(*args, **kwargs)

class About(models.Model):
    content = models.TextField()
    image = models.ImageField(upload_to='about/', blank=True, null=True)
    
    # Timestamps for SEO
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "About"
        verbose_name_plural = "About"
    
    def __str__(self):
        return "About Section"
    
    def save(self, *args, **kwargs):
        # Optimize image if provided
        if self.image:
            self.image = optimize_image(self.image)
        super().save(*args, **kwargs)

class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/', help_text="Recommended size: 1200x630px for optimal social media sharing")
    link = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order to display projects")
    
    # SEO fields
    meta_title = models.CharField(max_length=60, blank=True, null=True, 
                                help_text="Title for search engines (max 60 characters)")
    meta_description = models.CharField(max_length=160, blank=True, null=True, 
                                      help_text="Description for search engines (max 160 characters)")
    meta_keywords = models.CharField(max_length=200, blank=True, null=True,
                                   help_text="Keywords for search engines (comma separated)")
    
    # Timestamps for SEO
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Return the absolute URL for this project"""
        return reverse('project_detail', kwargs={'project_id': self.id})
    
    def save(self, *args, **kwargs):
        # Optimize project image
        if self.image:
            self.image = optimize_image(self.image)
        
        # Auto-generate meta fields if not provided
        if not self.meta_title:
            self.meta_title = self.title[:60]
            
        if not self.meta_description:
            self.meta_description = self.description[:157] + "..."
            
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['order']

class Technology(models.Model):
    name = models.CharField(max_length=50)
    project = models.ForeignKey(Project, related_name='technologies', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Technologies"

class TechnicalSkill(models.Model):
    name = models.CharField(max_length=50)
    percentage = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order']

class SoftSkill(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class (e.g. 'fa-users')")
    
    def __str__(self):
        return self.name

class Experience(models.Model):
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.CharField(max_length=20, help_text="e.g. '2020'")
    end_date = models.CharField(max_length=20, help_text="e.g. '2022' or 'Present'")
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    
    # Timestamps for SEO
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']
