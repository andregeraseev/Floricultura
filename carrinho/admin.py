from django.contrib import admin
from .models import ShoppingCart, ShoppingCartItem, Cupom
from django.contrib.sessions.models import Session

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'expire_date']
    # Você pode adicionar mais campos conforme necessário

# Admin para ShoppingCart
class ShoppingCartItemInline(admin.TabularInline):
    model = ShoppingCartItem
    extra = 1

class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'session', 'total', 'created_at', 'updated_at')
    inlines = [ShoppingCartItemInline]

# Admin para ShoppingCartItem
class ShoppingCartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')
    search_fields = ('cart__user_profile__user__username', 'product__name')
    list_filter = ('product',)

# Admin para Cupom
class CupomAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'desconto_percentual', 'maximo_usos', 'usos_atuais', 'status', 'data_validade')
    search_fields = ('codigo',)
    list_filter = ('status', 'data_validade')

# Registra no admin do Django
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(ShoppingCartItem, ShoppingCartItemAdmin)
admin.site.register(Cupom, CupomAdmin)
from django.contrib import admin

# Register your models here.
