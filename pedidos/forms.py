from django import forms

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
        choices=[('pac', 'PAC'), ('sedex', 'SEDEX')],
        widget=forms.RadioSelect,
        label='Frete'
    )
    coupon = forms.CharField(required=False, label='Cupom de Desconto')

    def __init__(self, *args, **kwargs):
        print('initial')
        super(CheckoutForm, self).__init__(*args, **kwargs)
        print(kwargs,args)
        try:
            user = kwargs.get('initial').get('user')
        except:
            user = None
        if user and user.is_authenticated:
            print(user.email)
            self.fields['email_pedido'].initial = user.email
