from carrinho.models import ShoppingCart
from django.shortcuts import render
from products.models import Product, Department, Category
from site_config.models import SocialLink, ContactInfo,UsefulLink,SiteSettings

from collections import defaultdict
from django.contrib.sessions.models import Session


def get_cart(request):
    # Certifique-se de que existe uma chave de sessão
    # print('iniciando contexto global')
    if not request.session.session_key:
        # print('Criando sessão ', request.session.session_key)
        request.session.create()
        session = request.session.session_key
        # print(session, 'criada')
    else:
        # print('Sessão existente', request.session.session_key)
        session = request.session.session_key

    # Se o usuário estiver autenticado, obtenha ou crie um carrinho associado ao perfil do usuário
    try:
        if request.user.is_authenticated and request.user.profile:
            # print('userautenticado', request.user)
            cart, created = ShoppingCart.objects.get_or_create(user_profile=request.user.profile)
            # print(cart, created, )
            # print('sessao', session)
            session_cart = ShoppingCart.objects.filter(session__session_key=session).first()
            # print(session_cart)
        else:
            session = Session.objects.get(session_key=session)
            cart, created = ShoppingCart.objects.get_or_create(session=session)
    except:
        print('erro ao criar carrinho para usuario autenticado')

        # Para usuários anônimos, obtenha ou crie um carrinho com base na sessão

        # print('session', session)
        session = Session.objects.get(session_key=session)
        cart, created = ShoppingCart.objects.get_or_create(session=session)
        # print(cart, created)

    return cart


def global_context(request):
    if request.user.is_authenticated:
        wishlist_product_ids = request.user.profile.wishlist.values_list('product_id', flat=True)
        favorite_counter = request.user.profile.wishlist.count()

    else:
        wishlist_product_ids = []
        favorite_counter = 0
    cart=get_cart(request)

    site_setting = SiteSettings.objects.first()

    categories = Category.objects.all()
    departements = Department.objects.all()
    # Buscar dados dos modelos
    social_links = SocialLink.objects.all()
    footer_info = ContactInfo.objects.first()  # Assumindo uma única instância
    # Organizar os links úteis por categoria
    useful_links_raw = UsefulLink.objects.all()
    footer_links = defaultdict(list)
    for link in useful_links_raw:
        footer_links[link.category].append(link)
    # Preparar o contexto com os dados para o template
    context = {
        'favorite_counter': favorite_counter,
        'cart': cart,
        'departements': departements,
        'site_setting': site_setting,
        'categories': categories,
        'social_links': social_links,
        'footer_info': footer_info,
        'footer_links': dict(footer_links),
        'wishlist_product_ids': wishlist_product_ids,
    }

    # Renderizar o template com o contexto

    return context