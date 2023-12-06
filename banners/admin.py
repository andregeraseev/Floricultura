from django.contrib import admin

from django.contrib import admin
from .models import HeroBanner, SecondaryBanner, BannerClick

@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(SecondaryBanner)
class SecondaryBannerAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(BannerClick)
class BannerClickAdmin(admin.ModelAdmin):
    list_display = ['content_object', 'clicked_at', 'clicked_by']
