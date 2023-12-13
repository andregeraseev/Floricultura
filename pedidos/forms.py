from django import forms
from pedidos.correios import cotacao_frete_correios


class CheckoutForm(forms.Form):
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
        choices=[('cartao_credito', 'Cartão de Crédito'), ('boleto', 'Boleto'), ('paypal', 'PayPal')],
        label='Método de Pagamento'
    )

    frete = forms.ChoiceField(
        choices=[],  # Inicialmente vazio
        widget=forms.RadioSelect,
        label='Frete'

    )
    coupon = forms.CharField(required=False, label='Cupom de Desconto')

    def clean_frete(self):
        print('clean_frete')
        frete = self.cleaned_data.get('frete')
        if not frete:
            raise forms.ValidationError('Por favor, escolha uma opção de frete.')

        # Divide o valor do frete em código do serviço e valor
        codigo_servico, valor_frete_enviado = frete.split('-')
        valor_frete_enviado = float(valor_frete_enviado)
        print(codigo_servico, valor_frete_enviado)

        # Verificar se o frete enviado corresponde a uma das opções válidas
        opcoes_validas = dict(self.fields['frete'].choices)
        print(opcoes_validas)
        if frete not in opcoes_validas:
            raise forms.ValidationError('A opção de frete selecionada é inválida.')

        return frete

    def __init__(self, *args, **kwargs):
        print('initial')
        print(kwargs, args)
        frete_choices = kwargs.pop('frete_choices', [])
        super(CheckoutForm, self).__init__(*args, **kwargs)
        self.fields['frete'].choices = frete_choices
        print(kwargs,args)
        try:
            user = kwargs.get('initial').get('user')
        except:
            user = None
        if user and user.is_authenticated:
            print(user.email)
            self.fields['email_pedido'].initial = user.email
        if 'frete_choices' in kwargs:
            self.fields['frete'].choices = kwargs.pop('frete_choices')

