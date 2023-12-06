from django import forms
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
from .models import ShoppingCartItem

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
