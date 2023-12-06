from django.shortcuts import render
from django.views import View
from products.models import Product


class ProductView(View):


    def get(self, request, slug):
        produto = Product.objects.get(slug=slug)
        return render(request, 'shop-details.html', context={'produto': produto})
