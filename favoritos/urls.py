from django.urls import path
from .views import AdicionarFavoritoView, FavoritosView

urlpatterns = [
    # ... suas outras urls ...
    path('adicionar-favorito/', AdicionarFavoritoView.as_view(), name='adicionar-favorito'),
    path('', FavoritosView.as_view(), name='favoritos'),
]
