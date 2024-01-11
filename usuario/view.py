from carrinho.models import ShoppingCart
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import json
import logging

from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from enviadores.email import enviar_email_confirmacao
from pedidos.models import Order

logger = logging.getLogger('usuarios')



def login_view(request):
    return render(request, 'login.html')

def logout_view(request):
    usuario = request.user.username
    logout(request)
    logger.info(f'Usuário {usuario} deslogado com sucesso')

    return redirect('home')

@csrf_exempt
def user_login(request):
    """
    Manipula o login do usuário, incluindo a transferência de itens do carrinho
    de compras de uma sessão anônima para a sessão do usuário autenticado.
    :param request: Objeto HttpRequest
    :return: JsonResponse com o status de sucesso e mensagem
    """
    print('user_login')

    if request.method != 'POST':
        logger.warning('Tentativa de login com método HTTP inválido')
        return JsonResponse({'success': False, 'message': 'Método inválido.'})

    try:
        data = json.loads(request.body)
        print(request.body)
        username = data.get('username')
        password = data.get('password')
        print('username',username)
        print('password',password)
        try:
            login_response = login_with_cart(password, request, username)
            return JsonResponse(login_response)

        except Exception as e:
            print('erros',e)
            logger.error('erros',e)
            return JsonResponse({'success': False, 'message': f'Erro interno do servidor. {e}'})



    except json.JSONDecodeError:
        logger.error('Erro na decodificação JSON durante o login')
        return JsonResponse({'success': False, 'message': 'Erro no processamento dos dados.'})
    except Exception as e:
        logger.error(f'Erro no processo de login: {e}')
        return JsonResponse({'success': False, 'message': 'Erro interno do servidor.'})


def login_with_cart(password, request, username):
    User = get_user_model()
    try:
        user = User.objects.get(email=username)
    except:
        try:
            user = authenticate(request, username=username, password=password)
        except:
            return {'success': False, 'message': 'Usuário ou senha inválidos.'}

    user = authenticate(request, username=user.username, password=password)
    if user is None:
        print(f'{username} user is None')
        logger.info(f'Tentativa de login falhou para o usuário {username}')
        return {'success': False, 'message': 'Usuário ou senha inválidos.'}
    else:
        logger.info(f'Usuário {username} autenticado com sucesso')
    # Tenta recuperar a sessão anônima e seu carrinho
    logger.info('incializando a função verifica_carrinho_session')
    session_cart, session_cart_items = verifica_carrinho_session(request)
    # Realiza o login, criando uma nova sessão
    login(request, user)
    logger.info(f'Usuário {username} logado com sucesso')
    # Recupera ou cria o carrinho para o usuário logado
    user_cart, created = ShoppingCart.objects.get_or_create(user_profile=user.profile)
    logger.info('incializando a função transferir_itens_carrinho_anonimo_carrinho_usuario')
    try:
        trransferir_itens_carrinho_anonimo_carrinho_usuario(session_cart, session_cart_items, user_cart)
        return {'success': True, 'message': 'Login realizado com sucesso.'}
    except Exception as e:
        logger.error(f'Erro ao transferir itens do carrinho: {e}')
        return {'success': False, 'message': 'Erro ao transferir itens do carrinho.'}

def verifica_carrinho_session(request):
    """""""""
    Verifica se existe um carrinho de compras e itens de uma sessão anônima.
    e guarda em uma variável.
    :param request: Objeto HttpRequest
    :return: Instância do ShoppingCart e lista de ShoppingCartItem
    """""""""

    try:
        session_cart = ShoppingCart.objects.filter(
            session__session_key=request.session.session_key
        ).first()
        session_cart_items = list(session_cart.items.all()) if session_cart else []

        if not session_cart:
            logger.info('Nenhum carrinho de sessão anônima para transferir')

    except ObjectDoesNotExist:
        logger.info('Sessão anônima não encontrada ao tentar transferir carrinho')
        session_cart = None
        session_cart_items = []
    return session_cart, session_cart_items


def trransferir_itens_carrinho_anonimo_carrinho_usuario(session_cart, session_cart_items, user_cart):
    """
    Transfere os itens do carrinho de uma sessão anônima para o carrinho do usuário logado.

    :param session_cart:
    :param session_cart_items:
    :param user_cart:
    :return:

    """

    for item_anonimo in session_cart_items:
        try:
            item_logado = user_cart.items.filter(
                product=item_anonimo.product,
                variation=item_anonimo.variation
            ).first()

            if item_logado:
                item_logado.quantity += item_anonimo.quantity
                item_logado.save()
            else:
                item_anonimo.cart = user_cart
                item_anonimo.save()
        except Exception as e:
            logger.error(f'Erro ao transferir item do carrinho: {e}')
    # Limpa o carrinho anônimo após a transferência
    if session_cart:
        session_cart.delete()
        logger.info(f'Transferência realizada com sucesso para o {user_cart} e carrinho de sessão anônima excluído')

from .forms import AddressForm, UserPhoneForm
from django.views import View
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm

class UserRegistrationView(View):
    def get(self, request, *args, **kwargs):
        print(request.user)
        form = UserRegistrationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('UserRegistrationform valido', form)
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')  # Pega a senha do formulário
            print('indo fazer login')
            try:
                enviar_email_confirmacao(form.cleaned_data.get('email'),form.cleaned_data.get('username'))
            except Exception as e:
                print('erros',e)

            login_with_cart(password =password, request=request, username=username)
            # Redirecionar para a página de login ou outra página conforme necessário
            return redirect('address_register')
        print('UserRegistrationform invalido',form)
        return render(request, 'register.html', {'form': form})





class AddressRegistrationView(View):
    def get(self, request, *args, **kwargs):
        print('request',request)
        print('args',args)
        print('kwargs',kwargs)
        kwargs = {'user': request.user}

        endereco_id = request.GET.get('endereco_id', None)
        requisicao_json = request.GET.get('requisicao_json', 'false').lower() == 'true'

        print('endereco_id', endereco_id)
        print('requisicao_json', requisicao_json)
        if requisicao_json == True:
            if endereco_id != '':
                endereco = request.user.profile.addresses.get(id=endereco_id)
                print('endereco', endereco)
                form = AddressForm(instance=endereco)
                adicionar_endereco = False
            else:
                form = AddressForm(initial=kwargs)
                adicionar_endereco = True
            form_html = render_to_string('usuario/editar-endereco-container.html', {'form': form}, request)
            return JsonResponse({'success': True, 'form_html': form_html, 'adicionar_endereco': adicionar_endereco})
        else:
            form = AddressForm(initial=kwargs)
            return render(request, 'add_address.html', {'form': form})


    def post(self, request, *args, **kwargs):
        content_type = request.META.get('CONTENT_TYPE')

        if content_type == 'application/json':
            # Requisição veio via AJAX
            data = json.loads(request.body.decode('utf-8'))  # Decodifica o corpo da requisição
            form = AddressForm(data)
            if form.is_valid():
                print('Adressform valido')
                try:
                    address = form.save(commit=False)
                    address.user_profile = request.user.profile
                    address.save()
                    return JsonResponse({'success': True, 'message': f'Endereço {address} adicionado.'})

                except Exception as e:
                    print('erros',e)
                    form_html = render_to_string('usuario/editar-endereco-container.html', {'form': form}, request)
                    return JsonResponse({'success': False, 'formulario_invalido': True, 'form_html': form_html})

        else:
            # Requisição veio via formulário HTML tradicional
            form = AddressForm(request.POST)
            if form.is_valid():
                try:
                    address = form.save(commit=False)
                    address.user_profile = request.user.profile
                    address.save()
                    return redirect('home')
                except Exception as e:
                    return render(request, 'add_address.html', {'form': form})

        print('Adressform invalido')
        return render(request, 'add_address.html', {'form': form})





    def delete(self, request, *args, **kwargs):
        print('request',request.body)
        print('args',args)
        print('kwargs',kwargs)
        try:
            data= json.loads(request.body)
            print('data',data)
            print('endereco_id',data.get('endereco_id'))
            endereco = request.user.profile.addresses.get(id=data.get('endereco_id'))
            print('endereco',endereco)
            endereco.delete()
            return JsonResponse({'success': True, 'message': 'Endereço excluído com sucesso.'})
        except ObjectDoesNotExist:
            return JsonResponse({'success': False, 'message': 'Endereço não encontrado.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro interno do servidor.{e}'})

    def put(self, request, *args, **kwargs):
        print('REQUISICAOPUT', request.body)
        try:
            data = json.loads(request.body)
            print('DATA', data)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Erro no processamento dos dados.'})
        try:
            # Remover tokens CSRF do objeto de dados
            data.pop('csrfmiddlewaretoken', None)

            endereco_id = data.get('endereco_id')
            endereco = request.user.profile.addresses.get(id=endereco_id)
            print('ENDERECO', endereco)

            form = AddressForm(data, instance=endereco)
            if form.is_valid():
                address = form.save(commit=False)
                address.user_profile = request.user.profile
                address.save()
                return JsonResponse({'success': True, 'message': f'Endereço {address} atualizado com sucesso.'})
            else:
                form_html = render_to_string('usuario/editar-endereco-container.html', {'form': form}, request)
                return JsonResponse({'success': False, 'formulario_invalido':True, 'form_html': form_html})


        except ObjectDoesNotExist:
            return JsonResponse({'success': False, 'message': 'Endereço não encontrado.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro interno do servidor: {e}'})


class UserDashboard(View):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form_celular = UserPhoneForm(instance=request.user.profile)
        pedidos = request.user.profile.orders.all()
        context = {'cliente': request.user.profile,
                   'enderecos': request.user.profile.addresses.all(),
                   'produtos_favoritos': request.user.profile.get_wishlist_items(),
                   'produtos_avise': request.user.profile.get_avise_items(),
                   'form_celular': form_celular,
                   'pedidos': pedidos
                   }
        return render(request, 'usuario/dashboard.html',context)

    def put(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            form_celular = UserPhoneForm(data, instance=request.user.profile)
            form_html = render_to_string('usuario/informacoes_cliente.html', {'form_celular': form_celular},
                                         request=request)

            if form_celular.is_valid():
                form_celular.save()
                return JsonResponse({'success': True, 'message': 'Número de celular atualizado com sucesso.','form_html': form_html})
            else:
                return JsonResponse({'success': False, 'formulario_invalido': True, 'message': 'Dados inválidos.', 'form_html': form_html})

        except json.JSONDecodeError as e:
            return JsonResponse({'success': False, 'message': 'Erro ao processar os dados JSON: ' + str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Erro interno do servidor: ' + str(e)})



from django.shortcuts import get_object_or_404
class PedidoUserDetailView(View):
    def get(self, request, *args, **kwargs):
        print('request',request)
        print('args',args)
        print('kwargs',kwargs)
        session_param = request.GET.get('session', None)
        print('session_param',session_param)
        pedido_id = kwargs.get('pedido_id')
        if session_param:
            pedido = get_object_or_404(Order, id=pedido_id, session=session_param)
        else:
            pedido = get_object_or_404(Order, id=pedido_id, user_profile=request.user.profile)
        # pedido = request.user.profile.orders.get(id=pedido_id)
        context = {'pedido': pedido}
        return render(request, 'usuario/detalhes_pedido.html', context)


