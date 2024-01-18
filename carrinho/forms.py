from django import forms
from pedidos.models import Order
from products.models import Product, ProductVariation

class AddToCartForm(forms.Form):
    """
    Formulário Django para adicionar produtos ao carrinho de compras.

    - product_id: ID do produto a ser adicionado.
    - variant_id: ID da variação do produto, se houver.
    - quantity: Quantidade do produto a ser adicionada ao carrinho.
    """

    product_id = forms.IntegerField()
    variant_id = forms.IntegerField(required=False)
    quantity = forms.IntegerField(min_value=1)

    def clean_product_id(self):
        """
        Valida se o product_id fornecido corresponde a um produto existente.
        Levanta uma ValidationError se o produto não for encontrado.
        """
        product_id = self.cleaned_data.get('product_id')
        if not Product.objects.filter(id=product_id).exists():
            raise forms.ValidationError('Produto não encontrado.')
        return product_id

    def clean_variant_id(self):
        """
        Valida se o variant_id fornecido corresponde a uma variação existente do produto.
        Levanta uma ValidationError se a variação não for encontrada.
        """
        variant_id = self.cleaned_data.get('variant_id')
        if variant_id and not ProductVariation.objects.filter(id=variant_id).exists():
            raise forms.ValidationError('Variação de produto não encontrada.')
        return variant_id


from django import forms
from .models import ShoppingCartItem, Cupom


class RemoveItemForm(forms.Form):
    """
    Formulário Django para validar a remoção de um item do carrinho de compras.

    - item_id: ID do item a ser removido do carrinho.
    """
    item_id = forms.IntegerField()

    def clean_item_id(self):
        """
        Valida se o item_id fornecido corresponde a um item existente no carrinho.
        Levanta uma ValidationError se o item não for encontrado.
        """
        item_id = self.cleaned_data.get('item_id')
        if not ShoppingCartItem.objects.filter(id=item_id).exists():
            raise forms.ValidationError('Item do carrinho não encontrado.')
        return item_id


from django import forms
from .models import Cupom
from django.utils import timezone


class CupomForm(forms.Form):
    cupom = forms.CharField(
        label='Cupom de Desconto',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Cupom de Desconto'})
    )

    def check_max_uso_por_cliente(self, cupom):
        """
        Verifica se o cliente atual usou o cupom um número de vezes igual ou superior ao máximo permitido.
        """
        print('check_max_uso_por_cliente')
        user = self.initial.get('user')
        print('user',user)

        try:
            if user and cupom.max_uso_por_cliente:
                print('user',user)
                print('cupom',cupom.max_uso_por_cliente)
                uso_count = Order.objects.filter(user_profile=user.profile, cupom=cupom).count()
                print('uso_count',uso_count)
                return uso_count >= cupom.max_uso_por_cliente
        except user.DoesNotExist:
            raise forms.ValidationError('Cupom Valido apenas para clientes cadastrados')

        return False

    def check_minimo_compra(self, cupom):
        """
        Verifica se o valor total do pedido atende ao valor mínimo de compra exigido pelo cupom.
        """
        total_pedido = self.initial.get('total_pedido')
        if total_pedido and cupom.minimo_compra:
            return total_pedido >= cupom.minimo_compra
        return True

    def clean_cupom(self):
        """
        Valida se o cupom fornecido é válido e atende aos critérios do negócio.
        Levanta uma ValidationError se o cupom não for válido.
        """
        codigo = self.cleaned_data.get('cupom')

        try:
            print('codigo',codigo)
            cupom = Cupom.objects.get(codigo=codigo)

            if cupom.status != 'Ativo':

                raise forms.ValidationError('Cupom não está ativo.')

            if cupom.data_validade < timezone.now():
                raise forms.ValidationError('Cupom expirado.')

            if cupom.maximo_usos <= cupom.usos_atuais:

                raise forms.ValidationError('Cupom já foi utilizado o número máximo de vezes.')

            if self.check_max_uso_por_cliente(cupom):
                print('check_max_uso_por_cliente')
                raise forms.ValidationError('Limite de uso deste cupom por cliente atingido.')

            if not self.check_minimo_compra(cupom):
                print('check_minimo_compra')
                raise forms.ValidationError('O valor mínimo de compra para este cupom não foi atingido.')

            # Adicione outras validações conforme necessário.


            return cupom


        except Cupom.DoesNotExist:
            raise forms.ValidationError('Cupom não encontrado.')

