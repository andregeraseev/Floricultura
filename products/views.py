from django.db.models import Count
from django.shortcuts import render
from django.views import View
from pedidos.models import Order, OrderItem
from products.models import Product


class ProductView(View):


    def get(self, request, slug):
        produto = Product.objects.get(slug=slug)

        pedido_itens = OrderItem.objects.filter(product=produto)

        # Obtenha todos os pedidos que contêm o item em questão
        # Obtenha todos os pedidos que contêm o produto em questão
        orders = Order.objects.filter(items__in=pedido_itens, status__in=["pending"]).order_by().values_list(
            'id', flat=True).distinct()
        # print(("ORDERS",orders))
        # Obtenha todos os outros itens que aparecem nos mesmos pedidos que o item em questão
        related_item_ids = OrderItem.objects.filter(order__in=orders).exclude(product=produto).annotate(
            count=Count('product')).order_by('-count')
        # print(related_item_ids, "ITENS")
        related_items = Product.objects.filter(orderitem__in=related_item_ids).distinct()[:4]
        print(related_items, "RELATED ITENS")
        # Ordene o dicionário pelos valores em ordem decrescente para obter os itens mais comuns
        return render(request, 'shop-details.html', context={'produto': produto, 'related_items': related_items})
