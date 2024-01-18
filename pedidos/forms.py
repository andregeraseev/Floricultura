from carrinho.models import ShoppingCart, Cupom
from django import forms
from .models import Order
from pedidos.correios import cotacao_frete_correios


class CheckoutForm(forms.Form):
    cart_id = forms.CharField(widget=forms.HiddenInput(), required=False)

    email_pedido = forms.EmailField(
        label='E-mail para envio do pedido',
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'E-mail para envio do pedido'})
    )

    observacoes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Observações'
    )
    metodo_pagamento = forms.ChoiceField(
        choices=[('mercado_pago', 'Mercado Pago'), ('pix', 'PIX'), ('deposito', 'Depósito Bancário')],
        label='Método de Pagamento'
    )

    frete = forms.ChoiceField(
        choices=[],  # Inicialmente vazio
        widget=forms.RadioSelect,
        label='Frete'

    )


    def clean(self):
        cleaned_data = super().clean()
        print('cleaned_data',self.cleaned_data)
        cart_id = self.cleaned_data.get('cart_id')
        print('cart_id',cart_id)
        if cart_id:
            try:
                cart = ShoppingCart.objects.get(id=cart_id)
                if cart.items.count() == 0:
                    raise forms.ValidationError("Seu carrinho está vazio. Adicione itens antes de prosseguir.")
            except ShoppingCart.DoesNotExist:
                raise forms.ValidationError("Carrinho inválido.")


            try:
                cart = ShoppingCart.objects.get(id=cart_id)
                if cart.items.count() == 0:
                    raise forms.ValidationError("Seu carrinho está vazio. Adicione itens antes de prosseguir.")
                for item in cart.items.all():
                    print('item',item)
                    if item.variation:

                        variation = item.variation
                        print('variation',variation)
                    else:
                        variation = None
                    try:
                        cart.verifica_estoque_suficiente_para_adicao(item.product, variation, 0)
                    except Exception as e:
                        erro = str(e)
                        self.add_error(None, erro)

            except ShoppingCart.DoesNotExist:
                raise forms.ValidationError("Carrinho inválido.")

        else:
            raise forms.ValidationError("ID do carrinho não fornecido.")

        return cleaned_data

    def clean_frete(self):
        # print('clean_frete')
        frete = self.cleaned_data.get('frete')
        if not frete:
            raise forms.ValidationError('Por favor, escolha uma opção de frete.')

        # Divide o valor do frete em código do serviço e valor
        codigo_servico, valor_frete_enviado = frete.split('-')
        valor_frete_enviado = float(valor_frete_enviado)
        # print(codigo_servico, valor_frete_enviado)

        # Verificar se o frete enviado corresponde a uma das opções válidas
        opcoes_validas = dict(self.fields['frete'].choices)
        # print(opcoes_validas)
        if frete not in opcoes_validas:
            raise forms.ValidationError('A opção de frete selecionada é inválida.')

        return frete

    def __init__(self, *args, **kwargs):
        # print('initial')
        # print(kwargs, args)
        frete_choices = kwargs.pop('frete_choices', [])
        super(CheckoutForm, self).__init__(*args, **kwargs)
        self.fields['frete'].choices = frete_choices
        # print(kwargs,args)
        try:
            user = kwargs.get('initial').get('user')
        except:
            user = None
        if user and user.is_authenticated:
            print(user.email)
            self.fields['email_pedido'].initial = user.email
        if 'frete_choices' in kwargs:
            self.fields['frete'].choices = kwargs.pop('frete_choices')


from django.core.exceptions import ValidationError







class ComprovanteForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ComprovanteForm, self).__init__(*args, **kwargs)
        self.fields['comprovante'].required = True
        self.fields['comprovante'].label = 'Comprovante de Pagamento'
        self.fields['comprovante'].help_text = 'Envie o comprovante de pagamento para que possamos identificar seu pedido.'

    class Meta:
        model = Order
        fields = ['comprovante']



    def clean_comprovante(self):
        comprovante = self.cleaned_data.get('comprovante')

        # Verificar se o comprovante foi fornecido
        if not comprovante:
            print('comprovante nao enviado',comprovante)
            raise ValidationError('O upload do comprovante é obrigatório.')
        else:
            # Verificar se o arquivo possui o atributo 'content_type'
            if hasattr(comprovante, 'content_type'):
                # Validar o tipo de arquivo
                if not comprovante.content_type in ['image/jpeg', 'image/png']:
                    raise ValidationError('Apenas imagens JPEG e PNG são aceitas.')

                # Validar o tamanho do arquivo (2MB)
                if comprovante.size > 1024 * 1024 * 2:  # 2MB limit
                    raise ValidationError('O tamanho do arquivo não pode exceder 2MB.')
            else:
                # Se o arquivo não tiver 'content_type', é inválido
                raise ValidationError('Arquivo inválido.')

            return comprovante

