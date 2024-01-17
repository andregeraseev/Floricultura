from django.db import models
import uuid
from django.contrib.sessions.models import Session
from django.utils import timezone
from products.models import Product, Category, ProductVariation, MateriaPrima
from usuario.models import UserProfile
from pedidos.models import Order, OrderItem
from django.utils.translation import gettext_lazy as _
import logging
logger = logging.getLogger('carrinho')

class ShoppingCart(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carrinho de {self.user_profile.user.username if self.user_profile else 'Anonymous'} 'ID' { self.user_profile.id if self.user_profile else 'Anonymous'} Cart ID{self.id}"

    def get_cart(self):
        if self.user_profile:
            return ShoppingCart.objects.filter(user_profile=self.user_profile , session=None).first()
        else:
            return ShoppingCart.objects.filter(session=self.session , user_profile=None).first()
        return self

    @property
    def total(self):
        return sum(item.product_or_variation.price_or_promocional_price * item.quantity for item in self.items.all())

    def verifica_estoque_suficiente_para_adicao(self,product, variation, quantidade_adicional):
        print('verificandoestoque')
        if product.has_variations():
            print('variacao')
            produto_variacao = variation
            if produto_variacao.variation_materials.exists():
                materia_primas_ids = variation.variation_materials.values_list('materia_prima_id', flat=True)
                # Obter o consumo total de matéria-prima dos itens já no carrinho
                consumo_carrinho = {}
                items_carrinho = self.items.filter(variation__variation_materials__materia_prima_id__in=materia_primas_ids)

            else:
                self.verificar_estoque_produto_sem_materia_prima(product,variation, quantidade_adicional)
                return True
        else:
            print('produto')
            if product.product_materials.exists():
                produto_variacao = product
                materia_primas_ids = product.product_materials.values_list('materia_prima_id', flat=True)
                # Obter o consumo total de matéria-prima dos itens já no carrinho
                consumo_carrinho = {}
                items_carrinho = self.items.filter(product__product_materials__materia_prima_id__in=materia_primas_ids)
            else:
                self.verificar_estoque_produto_sem_materia_prima(product, variation, quantidade_adicional)
                return True

        for item in items_carrinho:
            for material in item.variation.variation_materials.all():
                consumo_carrinho[material.materia_prima_id] = consumo_carrinho.get(material.materia_prima_id, 0) + (
                            material.quantity_used * item.quantity)
                consumo_antigo_carrinho = consumo_carrinho[material.materia_prima_id]


        # Adicionar o consumo do novo item
        for material in produto_variacao.variation_materials.all():
            consumo_carrinho[material.materia_prima_id] = consumo_carrinho.get(material.materia_prima_id, 0) + (
                        material.quantity_used * quantidade_adicional)
            print('novo consume',consumo_carrinho)

        # Verificar estoque para cada matéria-prima
        materias_primas = MateriaPrima.objects.filter(id__in=materia_primas_ids)
        for materia_prima in materias_primas:
            print('materia_prima', materia_prima.stock > consumo_carrinho.get(materia_prima.id, 0))
            if materia_prima.stock < consumo_carrinho.get(materia_prima.id, 0):
                raise Exception(f'Materia prima insuficiente, voce ja tem  {consumo_antigo_carrinho} no carrinho e o '
                                f'estoque total eh de {materia_prima.stock }')

        return True


    def verificar_estoque_produto_sem_materia_prima(self, product, variation, quantidade_adicional):
        if variation:
            quantidade_no_carrinho = self.items.filter(variation=variation).aggregate(
                total_quantidade=models.Sum('quantity'))['total_quantidade'] or 0
            if variation.estoqueAtual < quantidade_adicional + quantidade_no_carrinho:
                raise Exception(f' ESTOQUE INSUFICIENTE: {variation} - estoque do produto é de {variation.estoqueAtual}un,  unidades no carrinho {quantidade_no_carrinho}, ')

        else:
            quantidade_no_carrinho = self.items.filter(product=product).aggregate(total_quantidade=models.Sum('quantity'))[
                                         'total_quantidade'] or 0
            if product.estoqueAtual < quantidade_adicional + quantidade_no_carrinho:
                raise Exception(f'ESTOQUE INSUFICIENTE: {product} - - estoque do produto é de {product.estoqueAtual}un,  unidades no carrinho {quantidade_no_carrinho},')

    def add_item(self, product, quantity=1, variant_id=None):

        variant = None
        if variant_id is not None:

            variant = product.variations.get(id=variant_id)  # pega variacao caso exista
            if not variant.stock_suficiente(quantity):
                logger.info(f'Item não adicionado ao  {self}: {product} - {variant}')
                raise Exception('Produto sem estoque')


        else:
            if not product.stock_suficiente(quantity):
                logger.info(f'Item não adicionado ao  {self}: {product} - {variant} ')
                raise Exception('Produto sem estoque')

        self.verifica_estoque_suficiente_para_adicao(product, variant, quantity)

        # Atualiza ou cria um item no carrinho de compras
        item, created = ShoppingCartItem.objects.update_or_create(
            cart=self, product=product, variation=variant)

        if created:
            item.quantity = quantity
        else:
            item.quantity += quantity
        item.save()

        logger.info(f'Item adicionado ao {self}: {item} id {item.id}, Quantidade: {quantity}')
        return item

    def remove_item(self, product_id):
        ShoppingCartItem.objects.filter(cart=self, product__id=product_id).delete()


    def update_item_quantity(self, product_id, quantity):
        item = ShoppingCartItem.objects.get(cart=self, product__id=product_id)
        item.quantity = quantity
        item.save()



    def clear(self):
        self.items.all().delete()

    @property
    def count_items_quantity(self):
        return sum(item.quantity for item in self.items.all())

    def finalize_purchase(self):

        if self.session:
            order = Order.objects.create(user_profile=self.user_profile, session=self.session, session_key=self.session.session_key)
        else:
            order = Order.objects.create(user_profile=self.user_profile, session=None, session_key=None)
        for item in self.items.all():
            try:
                item.product.add_sells(item.quantity)
                item.product_or_variation.remover_stock(item.quantity)
            except Exception as e:
                print(e)

            OrderItem.objects.create(
                order=order,
                product=item.product,
                variation=item.variation,
                quantity=item.quantity,
                price=item.product_or_variation.price_or_promocional_price
            )
        self.clear()
        return order

    class Meta:
        verbose_name = _('shopping cart')
        verbose_name_plural = _('shopping carts')


class ShoppingCartItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product_or_variation.name} - {self.quantity}"



    def add_item(self):
        if self.product_or_variation.has_stock:
            logger.info(f'Item adicionado ao  {self.cart}: {self}')
            self.save()
        else:
            logger.info(f'Item não adicionado ao  {self.cart}: {self}')
            raise Exception('Produto sem estoque')

    def delete_item(self):
        logger.info(f'Item removido do  {self.cart}: {self}')
        self.delete()

    @property
    def product_or_variation(self):
        if self.variation:
            return self.variation
        return self.product

    @property
    def total(self):
        return self.product_or_variation.price * self.quantity

    @property
    def total_price_or_promotional_price(self):
        return self.product_or_variation.price_or_promocional_price * self.quantity


    class Meta:
        verbose_name = _('shopping cart item')
        verbose_name_plural = _('shopping cart items')
        unique_together = ('cart', 'product', 'variation')


# Create your models here.
class Cupom(models.Model):
    STATUS_CHOICES = (
        ('Ativo', 'Ativo'),
        ('Inativo', 'Inativo'),
        ('Expirado', 'Expirado'),
        ('Utilizado', 'Utilizado'),
    )

    codigo = models.CharField(max_length=15, unique=True)
    desconto_percentual = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    maximo_usos = models.IntegerField(default=1)
    usos_atuais = models.IntegerField(default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Ativo')
    data_validade = models.DateTimeField(default=timezone.now)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_modificacao = models.DateTimeField(auto_now=True)
    estados_frete_gratis = models.CharField(max_length=100, blank=True, null=True,
                                            help_text="Estados para frete grátis, separados por vírgula")
    max_uso_por_cliente = models.PositiveIntegerField(default=None, null=True, blank=True,
                                                      help_text="Máximo de uso por cliente."
                                                                " Deixe em branco ou coloque None para uso ilimitado.")
    tipo_de_frete_gratis = models.CharField(max_length=100, blank=True, null=True,
                                            help_text="Escolha o tipo de fretes que seram gratis, separados por vírgula")
    desconto_percentual_frete = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    desconto_fixo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    minimo_compra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    produtos_aplicaveis = models.ManyToManyField(Product, blank=True)
    categorias_aplicaveis = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return self.codigo

    def gerar_codigo(self):
        self.codigo = str(uuid.uuid4().hex.upper()[:15])

    def esta_ativo(self):
        return self.status == 'Ativo'

    def pode_ser_utilizado(self, total=None, produto=None, categoria=None, estado_entrega=None, tipo_frete=None,
                           user=None):

        # Verifica status e validade
        if not self.esta_ativo():
            return False, "Cupom inativo ou expirado."
        if self.usos_atuais >= self.maximo_usos:
            return False, "Este cupom já foi totalmente utilizado."
        if timezone.now() > self.data_validade:
            return False, "Este cupom já expirou."

        # Verifica o limite mínimo de compra, se aplicável
        if total and not self.atende_limite_minimo(total):
            return False, "O valor total do pedido não atende ao mínimo necessário para usar este cupom."

        if self.max_uso_por_cliente:
            print("TESTEANDO USO MAX CLIENTE")
            from pedidos.models import Order

            usos_por_usuario = Order.objects.filter(user__email=user, cupom=self).count()
            print('usos_por_usuario:', usos_por_usuario)
            if usos_por_usuario >= self.max_uso_por_cliente:
                return False, 'Limite de uso do cupom atingido para este usuário.'

        # Verifica se o cupom é aplicável a um produto específico, se aplicável
        if produto and not self.aplicavel_a_produto(produto):
            return False, "Este cupom não é válido para o produto selecionado."

        # Verifica se o cupom é aplicável a uma categoria específica, se aplicável
        if categoria and not self.aplicavel_a_categoria(categoria):
            return False, "Este cupom não é válido para a categoria do produto selecionado."

        # Verifica se o cupom oferece frete grátis para o estado de entrega
        if estado_entrega and not self.aplicar_frete_gratis(estado_entrega):
            return False, "Este cupom não é válido para frete grátis no estado selecionado."

        # Verifica se o tipo de frete está entre os permitidos para frete grátis, se aplicável
        if tipo_frete and self.tipo_de_frete_gratis:
            tipos_permitidos = self.tipo_de_frete_gratis.split(',')
            if tipo_frete not in tipos_permitidos:
                return False, f"Este cupom só é válido para frete do tipo: {', '.join(tipos_permitidos)}."

        # Caso o usuário não tenha selecionado um tipo de frete, mas o cupom oferece frete grátis
        if self.tipo_de_frete_gratis and not tipo_frete:
            return False, "Por favor, selecione um tipo de frete para aplicar o cupom."

        return True, "Cupom aplicado com sucesso."

    def pode_ser_utilizado_finalizar_pedido(self, total=None, produto=None, categoria=None, estado_entrega=None,
                                            tipo_frete=None):
        """Verificacao para quando o cliente cliar em finalizar pedido para
         caso tenha mudado algo depois de aplicar o cupom"""
        # Verifica status e validade
        if not self.esta_ativo():
            return False, "Cupom inativo ou expirado."

        if timezone.now() > self.data_validade:
            return False, "Este cupom já expirou."

        # Verifica o limite mínimo de compra, se aplicável
        if total and not self.atende_limite_minimo(total):
            return False, "O valor total do pedido não atende ao mínimo necessário para usar este cupom."

        # Verifica se o cupom é aplicável a um produto específico, se aplicável
        if produto and not self.aplicavel_a_produto(produto):
            return False, "Este cupom não é válido para o produto selecionado."

        # Verifica se o cupom é aplicável a uma categoria específica, se aplicável
        if categoria and not self.aplicavel_a_categoria(categoria):
            return False, "Este cupom não é válido para a categoria do produto selecionado."

        # Verifica se o cupom oferece frete grátis para o estado de entrega
        if estado_entrega and not self.aplicar_frete_gratis(estado_entrega):
            return False, "Este cupom não é válido para frete grátis no estado selecionado."

        # Verifica se o tipo de frete está entre os permitidos para frete grátis, se aplicável
        if tipo_frete and self.tipo_de_frete_gratis:
            tipos_permitidos = self.tipo_de_frete_gratis.split(',')
            if tipo_frete not in tipos_permitidos:
                return False, f"Este cupom só é válido para frete do tipo: {', '.join(tipos_permitidos)}."

        # Caso o usuário não tenha selecionado um tipo de frete, mas o cupom oferece frete grátis
        if self.tipo_de_frete_gratis and not tipo_frete:
            return False, "Por favor, selecione um tipo de frete para aplicar o cupom."

        return True, "Cupom aplicado com sucesso."

    def adicionar_uso(self):
        self.usos_atuais += 1
        self.save()

    def aplicar_cupom(self, codigo_cupom):
        from pedidos.models import Order
        if not self.cupom:
            try:
                cupom = Cupom.objects.get(codigo=codigo_cupom)

                # Se max_uso_por_cliente não for None, verifique o uso
                if cupom.max_uso_por_cliente:
                    usos_por_usuario = Order.objects.filter(user=self.user, cupom=cupom).count()
                    if usos_por_usuario >= cupom.max_uso_por_cliente:
                        return False, 'Limite de uso do cupom atingido para este usuário.'

                if cupom.pode_ser_utilizado():
                    cupom.adicionar_uso()
                    self.cupom = cupom
                    self.save()
                    return True, 'Cupom aplicado com sucesso.'
                else:
                    return False, 'Cupom expirado ou limite de uso atingido.'
            except Cupom.DoesNotExist:
                return False, 'Cupom inválido.'
        else:
            return False, 'Já existe um cupom aplicado neste pedido.'

    def aplicar_frete_gratis(self, estado_entrega):

        if self:
            # Se estados_frete_gratis estiver vazio ou None, retorna True
            if not self.estados_frete_gratis:
                return True

            estados_frete_gratis = self.estados_frete_gratis.split(',')
            if estado_entrega in estados_frete_gratis:
                return True
        return False

    def aplicar_desconto(self, total):
        if self.desconto_percentual:
            valor_com_desconto = total * (1 - (self.desconto_percentual / 100))
            desconto = total - valor_com_desconto
            return desconto, valor_com_desconto
        elif self.desconto_fixo:
            valor_com_desconto = max(0, total - self.desconto_fixo)
            desconto = total - valor_com_desconto
            return desconto, valor_com_desconto
        return 0, total

    def aplicavel_a_produto(self, produto):
        if self.produtos_aplicaveis.exists():
            return produto in self.produtos_aplicaveis.all()
        return True

    def aplicavel_a_categoria(self, categoria):
        if self.categorias_aplicaveis.exists():
            return categoria in self.categorias_aplicaveis.all()
        return True

    def atende_limite_minimo(self, total):
        if self.minimo_compra:
            return total >= self.minimo_compra
        return True
