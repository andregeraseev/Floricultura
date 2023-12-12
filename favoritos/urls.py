from django.urls import path
from .views import AdicionarFavoritoView

urlpatterns = [
    # ... suas outras urls ...
    path('adicionar-favorito/', AdicionarFavoritoView.as_view(), name='adicionar-favorito'),
]
