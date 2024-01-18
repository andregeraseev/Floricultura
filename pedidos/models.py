from products.models import Product, ProductVariation
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
    session_key = models.CharField(max_length=40, blank=True, null=True)
    session = models.ForeignKey(Session, related_name='session_order_addresses', on_delete=models.SET_NULL, null=True,
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
    comprovante = models.ImageField(upload_to='comprovantes/', null=True, blank=True)
    mercadopago_link = models.CharField(max_length=200, blank=True, null=True)
    mercado_pago_id = models.CharField(max_length=100, blank=True, null=True)
    taxa_gateway = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=100)  # Ex: 'credit_card', 'paypal', 'bank_transfer'
    payment_status = models.CharField(max_length=100, default='pending')  # Ex: 'pending', 'completed', 'failed'
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total =models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Cupom de desconto
    coupon = models.CharField(max_length=100)
    cupom = models.ForeignKey('carrinho.Cupom', on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    observacoes = models.TextField(blank=True, null=True)
    em_producao = models.BooleanField(default=False)

    # tiny
    id_tiny = models.CharField(max_length=100, blank=True, null=True)

    def adicionar_valores(self):
        self.subtotal = sum([item.total for item in self.items.all()])
        self.total = self.final_total
        self.save()

    @property
    def printable_address(self):
        if self.complemento:
            return f" <strong>Destinatario:</strong> {self.destinatario} <br> <strong>Rua:</strong> {self.rua}, {self.numero}   <strong>Bairro:</strong> {self.bairro}<br><strong> Cidade:</strong> {self.cidade} - {self.estado} <br>  <strong>Complemento:</strong>{self.complemento}<br><strong>CEP:</strong> {self.cep}"
        else:
            return f" <strong>Destinatario:</strong> {self.destinatario} <br> <strong>Rua:</strong> {self.rua}, {self.numero}   <strong>Bairro:</strong> {self.bairro}<br><strong> Cidade:</strong> {self.cidade} - {self.estado} <br><strong>CEP:</strong> {self.cep}"

    @property
    def printable_order(self):
        return f"Pedido: {self.id} | Cliente: {self.destinatario} | Email: {self.email_pedido} | CPF: {self.cpf_destinatario} |<p>" \
               f" Total: {self.total} | Status: {self.status}"
    def __str__(self):
        return f"Order {self.id} "

    @property
    def togle_em_producao(self):
        if self.em_producao == False:
            self.em_producao = True
        else:
            self.em_producao = False
        self.save()
        return self.em_producao

    @property
    def final_total(self):
        total= max(Decimal('0.00'), Decimal(self.subtotal) - Decimal(self.discount) + Decimal(self.valor_frete))
        return round(total,2)

    @property
    def is_paid(self):
        return self.payment_status == 'completed'

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    property
    def str_comprovante(self):
        if self.comprovante:
            return str(self.comprovante.url)
        return ''

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Preço por unidade no momento da compra

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    @property
    def product_or_variation(self):
        if self.variation:
            return self.variation
        return self.product

    @property
    def price_or_promocional_price(self):
        return self.product_or_variation.price_or_promocional_price


    @property
    def total(self):
        return self.price * self.quantity

    @property
    def total_price_or_promotional_price(self):
        return self.product_or_variation.price_or_promocional_price * self.quantity


    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')

