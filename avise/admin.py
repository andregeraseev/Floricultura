from django.contrib import admin
from .models import AviseItem  # Ajuste o caminho conforme necessário

@admin.register(AviseItem)
class AviseItemAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'product', 'added_on', 'updated_on', 'email_sent', 'email_sent_on')
    list_filter = ('email_sent', 'added_on', 'updated_on')
    search_fields = ('user_profile__user__username', 'product__name')  # Ajuste os campos conforme os nomes no seu modelo
    list_editable = ('email_sent',)
    raw_id_fields = ('user_profile', 'product',)
    date_hierarchy = 'added_on'
    ordering = ('-added_on',)

    def view_on_site(self, obj):
        return obj.product.get_absolute_url  # Ajuste se o seu modelo de produto tiver um método diferente para obter a URL
