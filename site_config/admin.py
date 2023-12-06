from django.contrib import admin
from .models import SocialLink, ContactInfo,UsefulLink, SiteSettings

@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'icon_class')
    search_fields = ('name', )


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ('address', 'phone', 'email')


@admin.register(UsefulLink)
class UsefulLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'category')
    list_filter = ('category', )
    search_fields = ('title', 'category')



@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'contact_email', 'theme_color']