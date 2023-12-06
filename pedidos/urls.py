

from django.urls import path
from .views import PedidoView

pedido_view = PedidoView.as_view()

urlpatterns = [
    path('', pedido_view, name='checkout'),

]