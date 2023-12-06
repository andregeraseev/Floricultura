from products.models import Product
from usuario.models import UserProfile
from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from django.contrib.sessions.models import Session

class Order(models.Model):
    ESTADOS_BRASIL = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
        ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
        ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
        ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
    ]
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='orders',null=True,
                                blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=100, default='pending')  # Ex: 'pending', 'shipped', 'delivered'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Informações de envio
    session = models.ForeignKey(Session, related_name='session_order_addresses', on_delete=models.CASCADE, null=True,
                                blank=True)
    destinatario = models.CharField(max_length=50)
    email_pedido = models.EmailField(max_length=254, blank=True, null=True)
    cpf_destinatario = models.CharField(max_length=14,null=True, blank=True)
    rua = models.CharField(max_length=50)
    numero = models.CharField(max_length=5)
    bairro = models.CharField(max_length=30)
    cidade = models.CharField(max_length=50)
    complemento = models.CharField(max_length=30, blank=True, null=True)
    estado = models.CharField(choices=ESTADOS_BRASIL, max_length=2)
    cep = models.CharField(max_length=9)
    pais = models.CharField(max_length=50, default='Brasil')
    tipo_frete = models.CharField(max_length=50, default='PAC')
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rastreio = models.CharField(max_length=50, blank=True, null=True)

    # Informações de pagamento
    payment_method = models.CharField(max_length=100)  # Ex: 'credit_card', 'paypal', 'bank_transfer'
    payment_status = models.CharField(max_length=100, default='pending')  # Ex: 'pending', 'completed', 'failed'

    # Cupom de desconto
    coupon = models.CharField(max_length=100)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    observacoes = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Order {self.id} "

    @property
    def final_total(self):
        return max(Decimal('0.00'), self.total - self.discount)

    @property
    def is_paid(self):
        return self.payment_status == 'completed'

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Preço por unidade no momento da compra

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')

