

from django.urls import path
from .views import ProductView

produto_view= ProductView.as_view()

urlpatterns = [

    path('<slug:slug>', produto_view, name='produtos'),
]