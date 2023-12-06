from carrinho.models import ShoppingCart
from django.shortcuts import render, redirect
import json
import logging
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
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
         login_with_cart(password, request, username)
         return JsonResponse({'success': True, 'message': 'Login realizado com sucesso.'})
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
    user = authenticate(request, username=username, password=password)
    if user is None:
        logger.info(f'Tentativa de login falhou para o usuário {username}')
        return JsonResponse({'success': False, 'message': 'Usuário ou senha inválidos.'})
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
    logger.info('incializando a função trransferir_itens_carrinho_anonimo_carrinho_usuario')
    trransferir_itens_carrinho_anonimo_carrinho_usuario(session_cart, session_cart_items, user_cart)


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

from .forms import AddressForm
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

            login_with_cart(password =password, request=request, username=username)
            # Redirecionar para a página de login ou outra página conforme necessário
            return redirect('address_register')
        print('UserRegistrationform invalido',form)
        return render(request, 'register.html', {'form': form})





class AddressRegistrationView(View):
    def get(self, request, *args, **kwargs):
        kwargs = {'user': request.user}
        form = AddressForm(initial=kwargs)
        return render(request, 'add_address.html', {'form': form})


    def post(self, request, *args, **kwargs):
        form = AddressForm(request.POST)
        if form.is_valid():
            print('Adressform valido')
            try:
                address = form.save(commit=False)
                address.user_profile = request.user.profile
                address.save()
                return redirect('home')
            except Exception as e:
                print('erros',e)
                return render(request, 'add_address.html', {'form': form})

        print('Adressform invalido')
        return render(request, 'add_address.html', {'form': form})


