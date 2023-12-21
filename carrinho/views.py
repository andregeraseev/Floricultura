import json
import logging
from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from carrinho.models import ShoppingCart, ShoppingCartItem
from products.models import Product
from django.contrib.sessions.models import Session
from carrinho.forms import AddToCartForm, RemoveItemForm
from django.template.loader import render_to_string
logger = logging.getLogger('carrinho')

class CartView(View):
    """
    View do carrinho de compras para gerenciar as ações do carrinho, incluindo
    adicionar itens, remover itens e renderizar o carrinho.
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'shoping-cart.html')

    def post(self, request):
        """
        Lida com requisições POST para adicionar itens ao carrinho.
        Utiliza o AddToCartForm para validar os dados de entrada.
        """
        form = AddToCartForm(json.loads(request.body))
        if form.is_valid():
            try:
                product_id = form.cleaned_data.get('product_id')
                variant_id = form.cleaned_data.get('variant_id')
                quantity = form.cleaned_data.get('quantity')

                product = Product.objects.get(id=product_id)
                cart = self.get_user_cart(request)
                item = cart.add_item(product, quantity, variant_id)
                cart_counter_items = self.cart_counter_items(cart)
                cart_sidebar = self.cart_sidebar(request)
                cart_partial = render_to_string('partials/_cart.html', request=request)
                plural = 'unidades foram adicionadas' if quantity > 1 else 'unidade foi adicionada'
                return JsonResponse(
                    {'success': True, 'message': f' {item.product_or_variation.name} {quantity} {plural} ao carrinho', 'cart_counter_items': cart_counter_items, 'cart_sidebar': cart_sidebar, "cart_partial":cart_partial})
            except Exception as e:
                logger.error(f'Erro ao adicionar ao carrinho: {e}')
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        else:
            return JsonResponse({'success': False, 'error': form.errors}, status=400)

    def delete(self, request):
        """
        Lida com requisições DELETE para remover itens do carrinho de compras.
        Utiliza o RemoveItemForm para validar o item_id.
        """
        try:
            form = RemoveItemForm(json.loads(request.body))
            if form.is_valid():
                item_id = form.cleaned_data.get('item_id')
                item = ShoppingCartItem.objects.get(id=item_id)
                item.delete_item()

                cart = self.get_user_cart(request)
                cart_counter_items = self.cart_counter_items(cart)
                cart_sidebar = self.cart_sidebar(request)
                cart_partial = render_to_string('partials/_cart.html', request=request)

                logger.info(f"Item removido do carrinho: Item ID {item_id}")
                return JsonResponse(
                    {'success': True, 'message': f'{item.product_or_variation.name} foi removido do carrinho', 'cart_counter_items': cart_counter_items,
                     'cart_sidebar': cart_sidebar,"cart_partial":cart_partial})

            else:
                logger.warning("Tentativa de remover item do carrinho com dados inválidos")
                return JsonResponse({'success': False, 'error': form.errors}, status=400)

        except json.JSONDecodeError:
            logger.error('Erro na decodificação JSON')
            return JsonResponse({'success': False, 'error': 'Dados inválidos'}, status=400)
        except Exception as e:
            logger.error(f'Erro ao remover item do carrinho: {e}')
            return JsonResponse({'success': False, 'error': 'Erro interno do servidor'}, status=500)

    def patch(self, request, *args, **kwargs):
        data = json.loads(request.body)
        return self.update_quantity(request, data)

    def update_quantity(self, request, data):
        item_id = data.get('item_id')
        change = int(data.get('change'))
        cart = self.get_user_cart(request)
        cart_counter_items = self.cart_counter_items(cart)
        cart_sidebar = self.cart_sidebar(request)
        cart_partial = render_to_string('partials/_cart.html', request=request)
        try:
            item = ShoppingCartItem.objects.get(id=item_id)
            print('item',item.product)
            print('itemvariation',item.variation)

            cart.verifica_estoque_suficiente_para_adicao(item.product, item.variation, change)
            if change > 0 or (change < 0 and item.quantity > 1):
                item.quantity += change
                item.save()
                cart = self.get_user_cart(request)
                cart_counter_items = self.cart_counter_items(cart)
                cart_sidebar = self.cart_sidebar(request)
                cart_partial = render_to_string('partials/_cart.html', request=request)

                return JsonResponse({'success': True, 'message': 'Quantidade atualizada','cart_counter_items': cart_counter_items, 'cart_sidebar': cart_sidebar, "cart_partial":cart_partial})
            else:
                return JsonResponse({'success': False, 'error': 'Quantidade não pode ser menor que 1','cart_counter_items': cart_counter_items, 'cart_sidebar': cart_sidebar, "cart_partial":cart_partial}, status=400)
        except ShoppingCartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item não encontrado','cart_counter_items': cart_counter_items, 'cart_sidebar': cart_sidebar, "cart_partial":cart_partial}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e),'cart_counter_items': cart_counter_items, 'cart_sidebar': cart_sidebar, "cart_partial":cart_partial}, status=500)


    def get_user_cart(self, request):
        """
        Retorna o carrinho de compras do usuário.
        Cria um novo carrinho se não existir um para o usuário ou cria um carrinho de sessao caso o usuario for anonimo.
        """
        try:
            if request.user.is_authenticated:
                cart, created = ShoppingCart.objects.get_or_create(user_profile=request.user.profile)
                if created:
                    logger.info(f'Carrinho criado para o usuário: {request.user.username}')
                else:
                    logger.info(f'Carrinho existente obtido para o usuário: {request.user.username}')
            else:
                session_key = request.session.session_key or request.session.create()
                session = Session.objects.get(session_key=session_key)
                cart, created = ShoppingCart.objects.get_or_create(session=session)
                if created:
                    logger.info('Carrinho criado para a sessão anônima')
                else:
                    logger.info('Carrinho existente obtido para a sessão anônima')
            return cart
        except Exception as e:
            logger.error(f'Erro ao obter ou criar carrinho: {e}')
            raise e

    def cart_counter_items(self,cart):
        """
        Retorna um dicionário com a contagem total de itens e o valor total no carrinho.
        Para atualizar o contador de itens no carrinho de compras.
        """
        try:
            # cart = self.get_user_cart(request)
            count = cart.count_items_quantity
            total = cart.total
            return {'success': True, 'count': count, 'total': total}
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    def cart_sidebar(self, request):
        """
        Renderiza o HTML para o sidebar do carrinho de compras.
        para ser utilizado com AJAX.

        """
        html = render_to_string('partials/_cart_sidebar.html', request=request)
        return html

