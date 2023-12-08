

from django.urls import path
from .views import PedidoView, orders_view, orders_list, marcar_como_pago,visualizar_pedido,imprimir_selecionados

pedido_view = PedidoView.as_view()

urlpatterns = [
    path('', pedido_view, name='checkout'),
    path('orders_view/', orders_view, name='orders_view'),
    path('orders_view/orders_list/', orders_list, name='orders_list'),
    path('orders_view/marcar_como_pago/', marcar_como_pago, name='marcar_como_pago'),
    path('orders_view/visualizar_pedido/<int:order_id>/', visualizar_pedido, name='visualizar_pedido'),
    path('orders_view/imprimir_selecionados/', imprimir_selecionados, name='imprimir_selecionados'),


]