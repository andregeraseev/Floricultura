

from django.urls import path
from .views import AviseView

avise_view = AviseView.as_view()

urlpatterns = [
    path('', avise_view, name='avise'),
    # path('add_to_cart/', cart_view, name='add_to_cart'),
    # path('delete_item_cart/', cart_view, name='delete_item_cart'),
    # path('cart_counter_items/', cart_view, name='cart_counter_items'),
    # path('cart_sidebar/', cart_view, name='cart_sidebar'),
    # outras rotas
]