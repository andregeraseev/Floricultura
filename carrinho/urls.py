# # carrinho/urls.py
# from carrinho.views import add_to_cart, delete_item_cart, cart, cart_sidebar, cart_counter_items
# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('add_to_cart/', add_to_cart, name='add_to_cart'),
#     path('delete_item_cart/', delete_item_cart, name='delete_item_cart'),
#     path('cart/', cart, name='cart'),
#     path('cart_sidebar/', cart_sidebar, name='cart_sidebar'),
#     path('cart_counter_items/', cart_counter_items, name='cart_counter_items'),
#
#     # Adicione outras URLs específicas do app carrinho aqui
# ]

from django.urls import path
from .views import CartView

cart_view = CartView.as_view()

urlpatterns = [
    path('', cart_view, name='cart'),
    # path('add_to_cart/', cart_view, name='add_to_cart'),
    # path('delete_item_cart/', cart_view, name='delete_item_cart'),
    # path('cart_counter_items/', cart_view, name='cart_counter_items'),
    # path('cart_sidebar/', cart_view, name='cart_sidebar'),
    # outras rotas
]