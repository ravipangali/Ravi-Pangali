from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, About, Project, Technology, TechnicalSkill, SoftSkill, Experience

class TechnologyInline(admin.TabularInline):
    model = Technology
    extra = 1
    fields = ['name']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'email', 'location', 'created_at', 'social_links']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'title', 'email', 'location']
    readonly_fields = ['created_at', 'updated_at']

    def social_links(self, obj):
        links = []
        if obj.github:
            links.append('<span style="color:#333;background:#eaeaea;padding:2px 6px;border-radius:3px;">GitHub</span>')
        if obj.facebook:
            links.append('<span style="color:#fff;background:#3b5998;padding:2px 6px;border-radius:3px;">Facebook</span>')
        if obj.linkedin:
            links.append('<span style="color:#fff;background:#0077b5;padding:2px 6px;border-radius:3px;">LinkedIn</span>')
        if obj.instagram:
            links.append('<span style="color:#fff;background:#e4405f;padding:2px 6px;border-radius:3px;">Instagram</span>')
        return format_html(' '.join(links)) if links else '-'
    social_links.short_description = 'Social Links'

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ['content_preview', 'has_image', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['content']
    readonly_fields = ['created_at', 'updated_at']

    def content_preview(self, obj):
        return (obj.content[:100] + '...') if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Has Image'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'has_link', 'image_preview', 'created_at']
    list_filter = ['created_at', 'updated_at', 'order']
    list_editable = ['order']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TechnologyInline]

    def has_link(self, obj):
        return bool(obj.link)
    has_link.boolean = True
    has_link.short_description = 'Has Link'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:50px;max-width:50px;" />', obj.image.url)
        return 'No Image'
    image_preview.short_description = 'Image'

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'project_order']
    list_filter = ['project']
    search_fields = ['name', 'project__title']
    ordering = ['project__order', 'name']

    def project_order(self, obj):
        return obj.project.order
    project_order.short_description = 'Project Order'

@admin.register(TechnicalSkill)
class TechnicalSkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'percentage', 'order', 'progress_bar']
    list_filter = ['order']
    list_editable = ['percentage', 'order']
    search_fields = ['name']
    ordering = ['order']

    def progress_bar(self, obj):
        color = 'success' if obj.percentage >= 80 else 'warning' if obj.percentage >= 60 else 'info'
        return format_html(
            '<div style="width:100px;background:#eee;border-radius:3px;overflow:hidden;display:inline-block;">'
            '<div style="width:{}%;background:#28a745;height:12px;"></div></div> {}%',
            obj.percentage, obj.percentage
        )
    progress_bar.short_description = 'Progress'

@admin.register(SoftSkill)
class SoftSkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'icon_preview']
    search_fields = ['name', 'icon']
    ordering = ['name']

    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<i class="fa {}"></i> {}'.format(obj.icon, obj.icon))
        return '-'
    icon_preview.short_description = 'Icon Preview'

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'period', 'order', 'created_at']
    list_filter = ['created_at', 'updated_at', 'order']
    list_editable = ['order']
    search_fields = ['title', 'company', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['order']

    def period(self, obj):
        return f"{obj.start_date} - {obj.end_date}"
    period.short_description = 'Period'

# Custom admin site configuration
admin.site.site_header = "Ravi Pangali Portfolio Admin"
admin.site.site_title = "Portfolio Admin Portal"
admin.site.index_title = "Welcome to Portfolio Administration" 