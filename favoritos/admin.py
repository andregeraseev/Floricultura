from django.contrib import admin
from .models import WishlistItem

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'product', 'added_on')
    search_fields = ('user_profile__user__username', 'product__name')
    list_filter = ('added_on',)
    date_hierarchy = 'added_on'
    ordering = ('-added_on',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('user_profile', 'product')
        return queryset
