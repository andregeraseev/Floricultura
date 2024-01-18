from carrinho.models import ShoppingCart, ShoppingCartItem
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from enviadores.email import enviar_email_pedido_criado, enviar_email_rastreio
from pedidos.models import Order
from products.models import Product
from django.contrib.sessions.models import Session
from carrinho.forms import AddToCartForm, RemoveItemForm
from django.template.loader import render_to_string
import json
import logging
from django.views import View
from django.shortcuts import render, redirect,get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from tiny_webhook.envia_pedido import enviar_pedido_para_tiny
from usuario.forms import AddressForm
from usuario.models import Address
from pedidos.forms import CheckoutForm, ComprovanteForm
from pedidos.correios import cotacao_frete_correios
from mercadopago_pagamento.mercadopago_preference import cria_preferencia
from carrinho.forms import CupomForm
logger = logging.getLogger('pedido')

def adicionar_rastreio(request):
    print('adicionar_rastreio')
    order_id = json.loads(request.body).get('id')
    codigo_rastreio = json.loads(request.body).get('codigo_rastreio')
    print(order_id)
    print(codigo_rastreio)
    try:
        order = Order.objects.get(id=order_id)
        print(order)
        order.rastreio = codigo_rastreio
        order.save()
        print(order.rastreio)

        try:
            enviar_email_rastreio(order.email_pedido, order.destinatario, order, order.rastreio)
        except Exception as e:
            print('erros enviar_email_rastreio', e)

        return JsonResponse({'success': True, 'message': f'Codigo de rastreio {codigo_rastreio} adicionado com sucesso ao pedido {order}'})
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Pedido não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def toggle_producao(request):
    print('toggle_producao')
    try:
        order_id = json.loads(request.body).get('id')
    except Exception as e:
        logger.error(f'Erro ao obter ID do pedido: {e}')
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    print(order_id)
    try:
        order = Order.objects.get(id=order_id)
        print(order)
        order.togle_em_producao
        order.save()
        print(order.em_producao)
        return JsonResponse({'success': True, 'message': f'Produção do pedido {order} atualizada com sucesso'})
    except Order.DoesNotExist:
        logger.warning(f'Pedido não encontrado: {order_id}')
        return JsonResponse({'success': False, 'error': 'Pedido não encontrado'}, status=404)
    except Exception as e:
        logger.error(f'Erro ao atualizar produção do pedido: {e}')
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def mudar_endereco(request):
    print('mudar_endereco')
    adress_id = json.loads(request.body).get('endereco_id')
    print(adress_id)
    try:
        adress = Address.objects.get(id=adress_id)
        print(adress)
        adress.toggles_self_primary_and_others_not()
        adress.save()
        print(adress.is_primary)
        return JsonResponse({'success': True, 'message': f'Endereço atualizado {adress} com sucesso'})
    except Address.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Endereço não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

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
        request.GET.get('cart')
        cart = get_user_cart(request)
        kwargs = {'user': request.user}
        kwargs['cart_id'] = cart.id

        if request.user.is_authenticated:
            adress = request.user.profile.addresses.filter(is_primary=True).first()
        else:
            session = Session.objects.get(session_key=request.session.session_key)
            adress = Address.objects.filter(session=session, is_primary=True).first()

        form, form_cupom, form_pedido = self.create_forms(request, adress)
        return render(request, 'checkout.html', {
            'form': form,
            'adress': adress,
            'form_pedido': form_pedido,
            "form_cupom": form_cupom
        })

    def post(self, request, *args, **kwargs):

        form_type = request.POST.get('form_type')
        form_cupom = CupomForm()
        if request.user.is_authenticated:
            adress = request.user.profile.addresses.filter(is_primary=True).first()
            session = None
        else:
            session = Session.objects.get(session_key=request.session.session_key)
            adress = Address.objects.filter(session=session, is_primary=True).first()

        if form_type == 'remover_cupom':
            return self.remover_cupom(request)
        if form_type == 'address':
            return self.formulario_endereco(request, session, adress)
        elif form_type == 'order':
            return self.fomulario_pedido(request, session, adress)
        elif form_type == 'cupom':
            return self.fomulario_cupom(request, session, adress, **kwargs)
        else:
            return JsonResponse({'success': False, 'error': 'Formulário inválido'}, status=400)

    def fomulario_pedido(self, request,session,adress):
        form_cupom = CupomForm()
        response = cotacao_frete_correios(request, get_user_cart(request), adress)
        data = json.loads(
            response.content.decode('utf-8'))
        frete_choices = [
            (f"{item['codigo']}-{item['valor']}", f"{item['codigo']} - {item['valor']} - {item['prazodeentrega']}") for
            item in
            data.get('results', [])]

        form_pedido = CheckoutForm(request.POST, frete_choices=frete_choices)

        if form_pedido.is_valid():


            # Crie a ordem aqui com as informações do formulário e do carrinho
            if request.user.is_authenticated:
                user = request.user.profile
                session = None
                anonimo = False

                adress = request.user.profile.addresses.get(is_primary=True)

            else:
                session = Session.objects.get(session_key=request.session.session_key)
                user = None
                anonimo = True
                adress = Address.objects.filter(session=session, is_primary=True).first()
            cart = get_user_cart(request)

            if cart.cupom != None:

                print('request.POST', request.POST)
                cupom = {'cupom': cart.cupom.codigo}
                form_cupom = CupomForm(cupom, initial={'user': user.user, 'total_pedido': cart.total, })
                if form_cupom.is_valid():
                    print('form_cupom valido')
                    pass
                else:
                    print('form_cupom invalido')
                    print('cart.cupom', cart.cupom)
                    cart.cupom = None
                    cart.save()
                    return render(request, 'checkout.html', {'form_pedido': form_pedido,'adress':adress,'form_cupom': form_cupom,})


            try:
                order = cart.finalize_purchase()  # Converte os itens do carrinho em itens da ordem
            except Exception as e:
                print('erros finalize_purchase', e)
                return render(request, 'checkout.html', {'form_pedido': form_pedido,'adress':adress,'form_cupom':form_cupom})

            try:

                codigo_servico, valor_frete = form_pedido.cleaned_data['frete'].split('-')
                order.tipo_frete = codigo_servico
                order.valor_frete = float(valor_frete)
                order.email_pedido = form_pedido.cleaned_data['email_pedido']
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
                order.save()
                order.adicionar_valores()
                try:
                    mercadopagolink = cria_preferencia(request, order.total, order.id)
                    order.mercadopago_link = mercadopagolink
                    order.save()
                except Exception as e:
                    print('erros cria_preferencia', e)
                try:
                    enviar_email_pedido_criado(order.email_pedido, order.destinatario, order)
                except Exception as e:
                    print('erros enviar_email_pedido_criado', e)
                if cart.cupom != None:
                    cart.cupom = None
                    cart.save()
                if order.payment_method == 'mercado_pago':
                    return redirect(mercadopagolink)
                else :
                    return redirect('pagamento_deposito_pix', order.id)

            except Exception as e:
                print('erros', e)
                return render(request, 'checkout.html', {'form_pedido': form_pedido,'adress':adress,'form_cupom': form_cupom,})
            return redirect('home')
        else:
            return render(request, 'checkout.html', {'form_pedido': form_pedido, 'adress':adress,'form_cupom': form_cupom,})

    def formulario_endereco(self, request,session,adress):
        form_cupom = CupomForm()
        form = AddressForm(request.POST)
        if form.is_valid():
            print('Adressform valido')
            try:
                if request.user.is_authenticated:
                    user = request.user.profile
                    session = None
                else:
                    session_key = request.session.session_key
                    session = Session.objects.get(session_key=session_key)
                    user = None
                address = form.save(commit=False)

                print(request.session.session_key)
                print('sessao', session)
                print('adrerss', address)
                address.session = session
                address.user_profile = user
                print('adrersssesao', address.session)
                address.save()
                print('salvo')
                return redirect('checkout')
            except Exception as e:
                print('erros', e)
                return render(request, 'checkout.html', {'form': form, 'form_cupom':form_cupom})
        print('Adressform invalido')
        return render(request, 'checkout.html', {'form': form})

    def fomulario_cupom(self, request, session, adress, **kwargs):
        # Obtém as opções de frete sem alterações
        frete_choices = self.get_frete_choices(request, adress)
        print('request',request.POST)
        # Instancia o form_pedido sem passar o request.POST
        form_pedido = CheckoutForm(None, frete_choices=frete_choices)
        cart = get_user_cart(request)
        user = request.user
        total_pedido = cart.total
        # Tratamento do form_cupom permanece o mesmo
        form_cupom = CupomForm(request.POST, initial={'user': user, 'total_pedido': total_pedido})
        if form_cupom.is_valid():
            try:
                cart.cupom = form_cupom.cleaned_data['cupom']
                cart.save()
                return redirect('checkout')
            except Exception as e:
                print('erros', e)

        # Renderiza a resposta com form_pedido não validado
        return render(request, 'checkout.html', {
            'form_cupom': form_cupom,
            'adress': adress,
            'form_pedido': form_pedido
        })

    def create_forms(self, request, adress):
        # Lógica comum para criar e preencher formulários
        kwargs = {'user': request.user}
        if adress:
            kwargs['cart_id'] = get_user_cart(request).id
            form = AddressForm(initial=kwargs)
            form_cupom = CupomForm()
            frete_choices = self.get_frete_choices(request, adress)
            form_pedido = CheckoutForm(initial=kwargs, frete_choices=frete_choices)
        else:
            form = AddressForm(initial=kwargs)
            form_cupom = CupomForm()
            form_pedido = CheckoutForm(initial=kwargs)

        return form, form_cupom, form_pedido

    def get_frete_choices(self, request, adress):
        # Lógica para obter frete_choices
        try:
            response = cotacao_frete_correios(request, get_user_cart(request), adress)
            data = json.loads(response.content.decode('utf-8'))
            return [(f"{item['codigo']}-{item['valor']}",
                     f"{item['codigo']} - {item['valor']} - {item['prazodeentrega']}")
                    for item in data.get('results', [])]
        except Exception as e:
            print('erros cotacao_frete_correios', e)
            return []

    def remover_cupom(self, request):
        cart = get_user_cart(request)
        cart.cupom = None
        cart.save()
        return redirect('checkout')

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

@staff_member_required
def orders_view(request):
    # Aqui você pode adicionar qualquer contexto adicional necessário
    context = {}
    return render(request, 'dashboard_admin/pedidos.html', context)

import logging
from django.http import JsonResponse
from django.db.models import Q
from .models import Order

# Configuração do logging
logger = logging.getLogger(__name__)

# Constantes para nomes de colunas e valores padrão
COLUMN_NAMES = ['id', '_', 'destinatario', 'status', 'total', 'created_at', 'rastreio', '_','em_producao']
DEFAULT_DRAW = 1
DEFAULT_START = 0
DEFAULT_LENGTH = 10

def get_request_parameters(request):
    """
    Extrai e converte os parâmetros da requisição. Valida os valores recebidos.
    """
    try:
        draw = int(request.GET.get('draw', DEFAULT_DRAW))
        start = int(request.GET.get('start', DEFAULT_START))
        length = int(request.GET.get('length', DEFAULT_LENGTH))
        search_value = request.GET.get('search[value]', '')
        return draw, start, length, search_value
    except ValueError as e:
        logger.error(f"Erro na validação de parâmetros: {e}")
        raise ValueError("Parâmetros inválidos na requisição.")

def apply_filters(query, request):
    """
    Aplica filtros de status e produção à query.
    """
    status_filter = request.GET.get('status', None)
    producao_filter = request.GET.get('producao', None)

    if status_filter:
        query = query.filter(status=status_filter)
    if producao_filter:
        print(producao_filter)
        query = query.filter(em_producao=producao_filter == 'em_producao')

    return query

def apply_ordering(query, request):
    """
    Aplica ordenação à query com base nos parâmetros da requisição.
    """
    order_column = int(request.GET.get('order_colum', 0))
    order_direction = request.GET.get('order_dir', 'desc')
    order_column_name = COLUMN_NAMES[order_column]

    if order_direction == 'desc':
        order_column_name = f'-{order_column_name}'

    return query.order_by(order_column_name)

def apply_search(query, search_value):
    """
    Aplica filtragem de pesquisa à query.
    """
    if search_value.isdigit():
        return query.filter(Q(destinatario__icontains=search_value) | Q(id=search_value))
    else:
        return query.filter(Q(destinatario__icontains=search_value))

def serialize_orders(orders):
    """
    Serializa os dados dos pedidos para a resposta.
    """
    return [
        {
        'id':  order.id,
        'check':   f"""<input type='checkbox' class='order-checkbox' data-id='{order.id}'> <a href='visualizar_pedido/{order.id}' class='fa fa-eye' ><a>  <i class='fa fa-money-bill' onclick='abrir_modal("{order.comprovante.url}")' style='cursor: pointer;'></i>""" if order.comprovante else f"<input type='checkbox' class='order-checkbox' data-id='{order.id}'> <a href='visualizar_pedido/{order.id}' class='fa fa-eye' ><a>",
        'full_name': order.user_profile.user.get_full_name() if order.user_profile and order.user_profile.user.get_full_name() else order.destinatario,
        'status': order.status,
        'final_total': order.final_total,
        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # Formato de data
        'rastreio': order.rastreio or f"<input type='text' class='tracking-input' placeholder='Código de rastreio' id='tracking-{ order.id }'><button class='track-btn' data-id='{order.id}'onclick='adicionarCodigoRastreio({ order.id }, this)'>Adicionar</button>",
        'actions':  f"<button class='pay-btn' data-id='{order.id}'>PAGAR</button>  " if order.status == 'pending' or order.status == 'Pagamento em Analize'else f"<button class='btn-success' data-id='{order.id}' disabled>PAGO</button>  ",
        'producao': f"<input type='checkbox' class='producao-checkbox' data-id='{order.id}' onclick='alterarProducaoStatus({ order.id })' {'checked' if order.em_producao else ''}>",
        'details': f"<button class='details-btn' data-id='{order.id}'>Detalhes</button> <span class='badge bg-warning' data-action='observacao' title='observação:\n {order.observacoes}'>Obs</span> " if  order.observacoes  else f"<button class='details-btn' data-id='{order.id}'>Detalhes</button>",
                              'user_details': {

        'cpf': order.user_profile.cpf if order.user_profile else '',
        'phone_number': order.user_profile.phone_number if order.user_profile else '',
        'whatsapp': order.user_profile.whatsapp if order.user_profile else '',
        'email': order.user_profile.user.email if order.user_profile else '',
        'link_mercado_pago': order.mercadopago_link if order.mercadopago_link else '',
        'taxa_gateway': order.taxa_gateway if order.taxa_gateway else '0.00',
        'id_tiny': order.id_tiny if order.id_tiny else '',}
        } for order in orders

    ]

def orders_list(request):
    """
    Função principal para listar pedidos com base nos parâmetros da requisição.
    """
    try:
        draw, start, length, search_value = get_request_parameters(request)

        query = Order.objects.all()
        query = apply_filters(query, request)
        filtered_total = query.count()  # Otimização para a contagem de registros filtrados
        query = apply_ordering(query, request)
        query = apply_search(query, search_value)

        orders = query[start:start + length]
        data = serialize_orders(orders)

        response = {
            'draw': draw,
            'recordsTotal': Order.objects.count(),
            'recordsFiltered': filtered_total,
            'data': data,
            'status': request.GET.get('status', None),
            'producao': request.GET.get('producao', None),
        }

        return JsonResponse(response)

    except Exception as e:
        logger.error(f"Erro ao listar pedidos: {e}")
        return JsonResponse({'error': 'Erro interno no servidor'}, status=500)


def marcar_como_pago(request):
    order_id = request.POST.get('order_id')
    try:
        order = Order.objects.get(id=order_id)
        order.status = 'pago'
        order.save()
        message = f'Pedido {order} marcado como pago, Porem não foi enviado para o tiny'
        try:
            messagem, id_tiny = enviar_pedido_para_tiny(order)
            order.id_tiny = id_tiny
            order.save()
        except Exception as e:
            print('erros enviar_pedido_para_tiny', e)

        return JsonResponse({'success': True, 'message': messagem})
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Pedido não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def visualizar_pedido(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()

    # Obter todas as localizações únicas dos itens
    localizacoes = set(item.product.localizacao if item.product.localizacao else "Sem Localização" for item in items)

    # Agrupar itens por localização
    items_por_localizacao = {localizacao: [] for localizacao in localizacoes}
    for item in items:
        if item.product.localizacao in localizacoes:
            items_por_localizacao[item.product.localizacao].append(item)
        else:
            items_por_localizacao['Sem Localização'].append(item)

    print(items_por_localizacao)



    return render(request, 'dashboard_admin/visualizar_pedido.html', {'order': order,'items_por_localizacao':items_por_localizacao})

@staff_member_required
def imprimir_selecionados(request):
    order_ids = request.GET.get('ids')

    orders = Order.objects.filter(id__in=order_ids.split(',') if order_ids else [])
    print('ordes',orders)
    context = {'orders': []}
    for order in orders:
        order = get_object_or_404(Order, id=order.id)
        items = order.items.all()

        # Obter todas as localizações únicas dos itens
        localizacoes = set(item.product.localizacao if item.product.localizacao else "Sem Localização" for item in items)
        print(localizacoes)
        # Agrupar itens por localização
        items_por_localizacao = {localizacao: [] for localizacao in localizacoes}
        print(items_por_localizacao)
        for item in items:
            if item.product.localizacao in localizacoes:
                items_por_localizacao[item.product.localizacao].append(item)
            else:
                items_por_localizacao['Sem Localização'].append(item)
        print(items_por_localizacao)
        context['orders'].append({'order': order, 'items_por_localizacao': items_por_localizacao})
    print(context)



    return render(request, 'dashboard_admin/imprimir_selecionados.html', context)


class MercadoPagoView(View):
    def get(self, request):
        print(request.GET)
        status = request.GET.get('status')
        external_reference = request.GET.get('external_reference')
        print(external_reference)
        return render(request, 'pagamento/mercado_pago_retorno.html', {'status': status, 'pedido_id':external_reference })


    def post(self, request):
        return render(request, 'pagamento/mercadopago.html')


class PagamentoDepositoPixView(View):
    def get(self,  request, order_id):
        print("order_id",order_id)
        form = ComprovanteForm()
        order = Order.objects.get(id=order_id)

        # Verificar se o pedido pertence ao usuário logado ou à sessão do usuário
        if request.user.is_authenticated:
            print('autorizado')
            if order.user_profile != request.user.profile:
                print('redirecionando')
                return redirect('home')
        else:
            print('nao autorizado')
            session_key = request.session.session_key
            session = Session.objects.get(session_key=session_key)
            print('sessao',session)
            print('order session',order.session)
            if order.session != session:
                print('redirecionando')

                return redirect('home')

        print("user eh igual", order.user_profile == request.user)
        print("sessao eh igual", order.session == request.session.session_key)
        return render(request, 'pagamento/pagamento_deposito_pix.html', {'order': order, 'form': form} )


    def post(self,request, order_id):
        from django.urls import reverse
        from django.contrib import messages

        order = get_object_or_404(Order, id=order_id)

        form = ComprovanteForm(request.POST, request.FILES, instance=order)
        if form.is_valid():
            form.save()
            order.status = 'Pagamento em Analize'
            order.save()
            # Obter o URL de referência
            referer_url = request.META.get('HTTP_REFERER')

            messages.success(request, 'Comprovante enviado com sucesso!')

            # Redirecionar para o referer ou para uma URL padrão
            return HttpResponseRedirect(referer_url if referer_url else reverse('home'))

        else:

            return render(request, 'pagamento/pagamento_deposito_pix.html', {'order': order, 'form': form})











