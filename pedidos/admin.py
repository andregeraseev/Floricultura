
from django.urls import reverse
from django.contrib import admin
from .models import Order, OrderItem
from django.utils.html import format_html


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Número de formulários em branco para novos itens


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('id', 'user_profile', 'status', 'em_producao', 'created_at', 'final_total', 'is_paid', 'view_items')
    list_editable = ('status', 'em_producao')
    list_filter = ('status', 'payment_method', 'created_at', 'estado')
    search_fields = ('id', 'user_profile__user__username', 'destinatario', 'cidade', 'cep')
    readonly_fields = ('created_at', 'updated_at', 'final_total', 'is_paid')
    fieldsets = (
        ('Informações Básicas', {'fields': ('user_profile', 'email_pedido','status', 'em_producao', 'total', 'discount', 'final_total', 'is_paid')}),
        ('Endereço de Envio', {'fields': ('tipo_frete','destinatario','cpf_destinatario', 'rua', 'numero', 'bairro', 'cidade', 'estado', 'cep', 'pais')}),
        ('Pagamento', {'fields': ('payment_method', 'payment_status', 'coupon')}),
        ('Outras Informações', {'fields': ('observacoes', 'created_at', 'updated_at')}),

    )

    def view_items(self, obj):
        items = obj.items.all()
        if items:
            return format_html('<br>'.join([f'{item.product.name} - Quantidade: {item.quantity}' for item in items]))
        return '-'
    view_items.short_description = 'Itens do Pedido'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total_item')
    list_filter = ('order__status', 'product')
    search_fields = ('order__id', 'product__name')

    def total_item(self, obj):
        return obj.quantity * obj.price
    total_item.short_description = 'Total'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order', 'product')
