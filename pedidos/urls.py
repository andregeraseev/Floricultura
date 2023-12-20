

from django.urls import path
from .views import PedidoView, orders_view, orders_list, marcar_como_pago,visualizar_pedido,imprimir_selecionados,\
    mudar_endereco, toggle_producao,adicionar_rastreio,MercadoPagoView,PagamentoDepositoPixView
from mercadopago_pagamento.mercadopago_webhook import MercadoPagoWebhook

pagamento_deposito_pix = PagamentoDepositoPixView.as_view()
mercadopago_webhook = MercadoPagoWebhook.as_view()
pedido_view = PedidoView.as_view()
mercadopago = MercadoPagoView.as_view()
urlpatterns = [
    path('', pedido_view, name='checkout'),
    path('mudar_endereco', mudar_endereco, name='mudar_endereco'),


    path('orders_view/', orders_view, name='orders_view'),
    path('orders_view/orders_list/', orders_list, name='orders_list'),
    path('orders_view/marcar_como_pago/', marcar_como_pago, name='marcar_como_pago'),
    path('orders_view/toggle_producao/', toggle_producao, name='toggle_producao'),
    path('orders_view/adicionar_rastreio/', adicionar_rastreio, name='adicionar_rastreio'),
    path('orders_view/visualizar_pedido/<int:order_id>/', visualizar_pedido, name='visualizar_pedido'),
    path('orders_view/imprimir_selecionados/', imprimir_selecionados, name='imprimir_selecionados'),

    # PAGAMENTOS
    path('pagamento/mercadopago/', mercadopago, name='pagamento_mercadopago'),
    path('mercadopago/pending', mercadopago, name='pagamento_mercadopago'),
    path('pagamento/mercadopago/failure', mercadopago, name='pagamento_mercadopago'),
    path('pagamento/mercadopago/pending', mercadopago, name='pagamento_mercadopago'),
    path('pagamento/mercadopago_webhook', mercadopago_webhook, name='mercadopago_webhook'),
    path('pagamento/pagamento_deposito_pix/<int:order_id>', pagamento_deposito_pix, name='pagamento_deposito_pix'),



]