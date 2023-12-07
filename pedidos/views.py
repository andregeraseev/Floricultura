from carrinho.models import ShoppingCart, ShoppingCartItem
from pedidos.models import Order
from products.models import Product
from django.contrib.sessions.models import Session
from carrinho.forms import AddToCartForm, RemoveItemForm
from django.template.loader import render_to_string
import json
import logging
from django.views import View
from django.shortcuts import render, redirect
from django.http import JsonResponse
from usuario.forms import AddressForm
from usuario.models import Address
from pedidos.forms import CheckoutForm
logger = logging.getLogger('pedido')


def get_user_cart(request):
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

class PedidoView(View):
    """
    View do carrinho de compras para gerenciar as ações do carrinho, incluindo
    adicionar itens, remover itens e renderizar o carrinho.
    """
    def get(self, request, *args, **kwargs):
        kwargs = {'user': request.user}
        form = AddressForm(initial=kwargs)
        form_pedido = CheckoutForm(initial=kwargs)
        if request.user.is_authenticated:
            adress = request.user.profile.addresses.filter(is_primary=True).first()
        else:
            session = Session.objects.get(session_key=request.session.session_key)
            adress = Address.objects.filter(session=session, is_primary=True).first()
            print(adress)


        return render(request, 'checkout.html', {'form': form , 'adress':adress, 'form_pedido':form_pedido})

    def post(self, request, *args, **kwargs):
        form_type = request.POST.get('form_type')

        if form_type == 'address':
            return self.formulario_endereco(request)
        elif form_type == 'order':
            return self.fomulario_pedido(request)
        else:
            return JsonResponse({'success': False, 'error': 'Formulário inválido'}, status=400)

    def fomulario_pedido(self, request):
        form_pedido = CheckoutForm(request.POST)
        if form_pedido.is_valid():
            # Crie a ordem aqui com as informações do formulário e do carrinho
            if request.user.is_authenticated:
                user = request.user.profile
                session = None
                adress = request.user.profile.addresses.get(is_primary=True)

            else:
                session = Session.objects.get(session_key=request.session.session_key)
                user = None
                adress = Address.objects.filter(session=session, is_primary=True).first()
                print(adress)
            cart = get_user_cart(request)
            order = cart.finalize_purchase()  # Converte os itens do carrinho em itens da ordem
            order.payment_method = form_pedido.cleaned_data['metodo_pagamento']
            order.observacoes = form_pedido.cleaned_data['observacoes']
            order.destinatario = adress.destinatario
            order.cpf_destinatario = adress.cpf_destinatario
            order.rua = adress.rua
            order.numero = adress.numero
            order.bairro = adress.bairro
            order.cidade = adress.cidade
            order.complemento = adress.complemento
            order.estado = adress.estado
            order.cep = adress.cep
            order.tipo_frete = form_pedido.cleaned_data['frete']

            order.save()

            return redirect('home')
        else:
            form = CheckoutForm()
        return render(request, 'checkout.html', {'form': form})

    def formulario_endereco(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            print('Adressform valido')
            try:
                address = form.save(commit=False)
                print(request.session.session_key)
                session_key = request.session.session_key
                session = Session.objects.get(session_key=session_key)
                print('sessao', session)
                print('adrerss', address)
                address.session = session
                print('adrersssesao', address.session)
                address.save()
                print('salvo')
                return redirect('checkout')
            except Exception as e:
                print('erros', e)
                return render(request, 'checkout.html', {'form': form})
        print('Adressform invalido')
        return render(request, 'checkout.html', {'form': form})

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

                logger.info(f"Item removido do carrinho: Item ID {item_id}")
                return JsonResponse(
                    {'success': True, 'message': 'Item removido com sucesso', 'cart_counter_items': cart_counter_items,
                     'cart_sidebar': cart_sidebar})

            else:
                logger.warning("Tentativa de remover item do carrinho com dados inválidos")
                return JsonResponse({'success': False, 'error': form.errors}, status=400)

        except json.JSONDecodeError:
            logger.error('Erro na decodificação JSON')
            return JsonResponse({'success': False, 'error': 'Dados inválidos'}, status=400)
        except Exception as e:
            logger.error(f'Erro ao remover item do carrinho: {e}')
            return JsonResponse({'success': False, 'error': 'Erro interno do servidor'}, status=500)

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


# views.py
from django.http import JsonResponse
from .models import Order


def orders_view(request):
    # Aqui você pode adicionar qualquer contexto adicional necessário
    context = {}
    return render(request, 'dashboard_admin/pedidos.html', context)

def orders_list(request):
    draw = int(request.GET.get('draw', default=1))
    start = int(request.GET.get('start', default=0))
    length = int(request.GET.get('length', default=10))

    # Processar a busca e os filtros
    search_value = request.GET.get('search[value]', default='')

    # Aqui você pode ajustar a consulta para filtrar os dados
    orders = Order.objects.filter(destinatario__icontains=search_value)[start:start + length]
    total = Order.objects.count()

    # Serializar os dados para JSON
    data = [{
        'id': order.id,
        'full_name': order.user_profile.user.get_full_name() if order.user_profile and order.user_profile.user.get_full_name() else order.destinatario,
        'status': order.status,
        'final_total': order.final_total,
        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # Formato de data
        'rastreio': order.rastreio or f"<input type='text' class='tracking-input' placeholder='Código de rastreio'><button class='track-btn' data-id='{order.id}'>Adicionar</button>",
        'actions': f"<button class='pay-btn' data-id='{order.id}'>Pago</button>",
        'details': f"<button class='details-btn' data-id='{order.id}'>Detalhes</button>",
                              'user_details': {
        'cpf': order.user_profile.cpf if order.user_profile else '',
        'phone_number': order.user_profile.phone_number if order.user_profile else '',
        'whatsapp': order.user_profile.whatsapp if order.user_profile else '',
        'email': order.user_profile.user.email if order.user_profile else '',}

         } for order in orders]

    # Construir a resposta
    response = {
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': total,
        'data': data,
    }

    return JsonResponse(response)



def marcar_como_pago(request):
    print('marcar como pago')
    order_id = request.POST.get('order_id')
    print(order_id)
    try:
        order = Order.objects.get(id=order_id)
        print(order)
        order.status = 'pago'
        order.save()
        print(order.status)
        return JsonResponse({'success': True, 'message': 'Pedido atualizado com sucesso'})
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Pedido não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

