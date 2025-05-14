from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Profile(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=150, help_text="Your professional title or role")
    avatar = models.ImageField(upload_to='profile/', blank=True, null=True)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=30, blank=True, null=True, help_text="Phone number (e.g. +1 234 567 8900)")
    location = models.CharField(max_length=100)
    
    # Social links
    github = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profile"
    
    def __str__(self):
        return self.name

class About(models.Model):
    content = models.TextField()
    image = models.ImageField(upload_to='about/', blank=True, null=True)
    
    class Meta:
        verbose_name = "About"
        verbose_name_plural = "About"
    
    def __str__(self):
        return "About Section"

class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/')
    link = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order to display projects")
    
    def __str__(self):
        return self.title
    
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
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']
