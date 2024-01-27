from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from pedidos.models import Order

from products.models import Product, Department, Category, ProductVariation, ProductMaterial
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from banners.models import HeroBanner, SecondaryBanner
from blog.models import Post
from django.db.models import Case, When, Value, F, Min, DecimalField
from django.db.models.functions import Coalesce
from django.db.models import Case, When, Value, BooleanField, F, Q, Exists, OuterRef
from rest_framework.utils import json
import logging
logger = logging.getLogger('usuarios')

def product_with_stock_order(base_query):
    # Condição para variação com estoque
    variation_stock_condition = Exists(
        ProductVariation.objects.filter(
            product_id=OuterRef('pk'),
            estoqueAtual__gt=0
        )
    )

    # Condição para variação com matéria-prima suficiente
    variation_material_condition = Exists(
        ProductVariation.objects.filter(
            product_id=OuterRef('pk'),
            variation_materials__materia_prima__stock__gte=F('variation_materials__quantity_used')
        )
    )

    # Condição para produto com matéria-prima suficiente
    material_stock_condition = ~Exists(
        ProductMaterial.objects.filter(
            product_id=OuterRef('pk'),
            materia_prima__stock__lt=F('quantity_used')
        )
    )

    # Anotação para verificar o estoque
    products_with_stock = base_query.annotate(
        has_stock_query=Case(
            When(variations__isnull=False, then=Case(
                When(variation_stock_condition, then=Value(True)),
                When(variation_material_condition, then=Value(True)),
                default=Value(False)
            )),
            When(product_materials__isnull=False, then=material_stock_condition),
            default=Case(
                When(estoqueAtual__gt=0, then=Value(True)),
                default=Value(False)
            ),
            output_field=BooleanField()
        )
    ).order_by('-has_stock_query', 'name').distinct()

    return products_with_stock


def product_with_stock_filter(base_query):
    # Condição para variação com estoque
    variation_stock_condition = Exists(
        ProductVariation.objects.filter(
            product_id=OuterRef('pk'),
            estoqueAtual__gt=0
        )
    )

    # Condição para variação com matéria-prima suficiente
    variation_material_condition = Exists(
        ProductVariation.objects.filter(
            product_id=OuterRef('pk'),
            variation_materials__materia_prima__stock__gte=F('variation_materials__quantity_used')
        )
    )

    # Condição para produto com matéria-prima suficiente
    material_stock_condition = ~Exists(
        ProductMaterial.objects.filter(
            product_id=OuterRef('pk'),
            materia_prima__stock__lt=F('quantity_used')
        )
    )

    # Anotação para verificar o estoque
    products_with_stock = base_query.annotate(
        has_stock_query=Case(
            When(variations__isnull=False, then=Case(
                When(variation_stock_condition, then=Value(True)),
                When(variation_material_condition, then=Value(True)),
                default=Value(False)
            )),
            When(product_materials__isnull=False, then=material_stock_condition),
            default=Case(
                When(estoqueAtual__gt=0, then=Value(True)),
                default=Value(False)
            ),
            output_field=BooleanField()
        )
    ).filter(has_stock_query=True).distinct()

    return products_with_stock

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta




def product_with_minimum_stock_filter(base_query):
    # Condição para variação abaixo do estoque mínimo
    variation_min_stock_condition = Exists(
        ProductVariation.objects.filter(
            product_id=OuterRef('pk'),
            estoqueAtual__lte=F('estoqueMinimo')
        )
    )

    # Condição para produto com matéria-prima abaixo do mínimo necessário
    material_min_stock_condition = Exists(
        ProductMaterial.objects.filter(
            product_id=OuterRef('pk'),
            materia_prima__stock__lt=F('quantity_used')
        )
    )

    # Anotação para verificar o estoque mínimo
    products_with_min_stock = base_query.annotate(
        below_min_stock_query=Case(
            When(variations__isnull=False, then=variation_min_stock_condition),
            When(product_materials__isnull=False, then=material_min_stock_condition),
            default=Case(
                When(estoqueAtual__lte=F('estoqueMinimo'), then=Value(True)),
                default=Value(False)
            ),
            output_field=BooleanField()
        )
    ).filter(below_min_stock_query=True).distinct()

    return products_with_min_stock
def products_stock_alert():
    products = Product.objects.all().prefetch_related('variations', 'product_materials',
                                                      'product_materials__materia_prima')
    lista_de_produtos_alerta_estoque = [{'nome' :product.name, 'quantidade_em_estoque' : product.quantidade_em_estoque,'vendas' : product.sells,} for product in products if product.stock_alert == True]
    lista_de_produtos_alerta_estoque = sorted(lista_de_produtos_alerta_estoque, key=lambda x: x['vendas'], reverse=True)[:10]

    logger.info(f'lista_de_produtos_alerta_estoque{lista_de_produtos_alerta_estoque}')
    return lista_de_produtos_alerta_estoque


def get_active_users_with_session_start_formatted():
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_sessions = {}

    # Obtendo a duração da sessão em segundos
    session_duration = settings.SESSION_COOKIE_AGE

    # Duração padrão de uma sessão em Django (modifique conforme sua configuração)
    session_duration = timedelta(seconds=session_duration)  # Exemplo: 1 hora

    for session in active_sessions:
        session_data = session.get_decoded()
        uid = session_data.get('_auth_user_id')
        if uid:
            try:
                user = User.objects.get(id=uid)
                # Estimativa do início da sessão
                session_start = session.expire_date - session_duration
                session_start_formatted = session_start.strftime("%d/%m/%Y")
                user_sessions[user] = session_start_formatted
            except User.DoesNotExist:
                continue
    print('user_sessions',user_sessions)
    return user_sessions



from django.db.models import Count
from django.db.models.functions import TruncDay
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User  # Substitua caso esteja usando um modelo de usuário customizado

def get_daily_user_registrations():
    # Calculando a data de início para os últimos 60 dias
    start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
    print('start_date',start_date)
    # Selecionando todos os perfis de usuário desde a data de início
    all_profiles = User.objects.filter(date_joined__gte=start_date)

    # Contando os registros de usuário por dia
    registration_data = all_profiles.annotate(day=TruncDay('date_joined')) \
                                    .values('day') \
                                    .annotate(daily_count=Count('id')) \
                                    .order_by('day')

    # Convertendo os dados em uma lista de contagens diárias
    daily_registrations_list = [(reg['day'], reg['daily_count']) for reg in registration_data]

    # Garantindo que todos os dias estejam representados
    daily_registrations_list = [(reg['day'].strftime("%d/%b"), reg['daily_count']) for reg in registration_data]
    daily_registrations_dict = {reg[0]: reg[1] for reg in daily_registrations_list}
    for day in (start_date + timedelta(days=n) for n in range(7)):
        formatted_day = day.strftime("%d/%b")
        daily_registrations_dict.setdefault(formatted_day, 0)

    return list(daily_registrations_dict.values()), list(daily_registrations_dict.keys())


from django.db.models import Count, Q
from pedidos.models import Order, OrderItem

def get_top_selling_products():
    produtos_mais_vendidos = Product.objects.all().order_by('-sells')[:10]
    produtos_mais_vendidos_dic = [{'nome': product.name, 'primeiraQuantidade': product.sells, 'segundaQuantidade': product.quantidade_em_estoque} for product in produtos_mais_vendidos]

    produtos_mais_vendidos_json = json.dumps(produtos_mais_vendidos_dic)

    # Obter a lista de vendas
    lista_de_vendas = produtos_mais_vendidos.values_list('sells', flat=True)

    # Somar a quantidade de vendas
    quantidade_de_vendas = sum(lista_de_vendas)
    print('quantidade_de_vendas',quantidade_de_vendas)
    return produtos_mais_vendidos_json, quantidade_de_vendas


from products.models import Product  # Substitua por seu modelo de vendas

from pedidos.models import Order
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Count
def get_monthly_sales():
    # Mapeamento de número do mês para nome do mês
    month_names = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    # Calculando a data de início para os últimos 12 meses
    start_date = timezone.now().replace(day=1) - timedelta(days=365)

    # Selecionando todas as ordens desde a data de início
    all_orders = Order.objects.filter(created_at__gte=start_date)

    # Agrupando as vendas por mês e somando os totais
    sales_data = all_orders.annotate(month=TruncMonth('created_at')) \
                           .values('month') \
                           .annotate(total_sales=Sum('total'), total_orders=Count('id')) \
                           .order_by('month')

    # Criando um dicionário com os totais de vendas por nome do mês
    monthly_sales_dict = {month_names[sale['month'].month]: int(sale['total_sales']) for sale in sales_data}
    monthly_orders_dict = {month_names[sale['month'].month]: sale['total_orders'] for sale in sales_data}
    # Garantindo que todos os meses estejam representados no dicionário
    for month in range(1, 13):
        monthly_sales_dict.setdefault(month_names[month], 0)
        monthly_orders_dict.setdefault(month_names[month], 0)

    print('monthly_sales_dict', monthly_sales_dict.values())

    return list(monthly_sales_dict.values()), list(monthly_sales_dict.keys()), list(monthly_orders_dict.values())


import time
def dashboard_graficos(request):
    logger.info('dashboard')

    # Iniciar o cronômetro para get_monthly_sales
    start_time = time.time()
    vendas, meses, vendas_mensais = get_monthly_sales()
    logger.info(f"get_monthly_sales executado em {time.time() - start_time} segundos")

    # Iniciar o cronômetro para get_daily_user_registrations
    start_time = time.time()
    usuarios_cadastrados, meses_cadastro = get_daily_user_registrations()
    logger.info(f"get_daily_user_registrations executado em {time.time() - start_time} segundos")

    # Iniciar o cronômetro para get_top_selling_products
    start_time = time.time()
    produtos_mais_vendidos, quantidade_de_vendas = get_top_selling_products()
    logger.info(f"get_top_selling_products executado em {time.time() - start_time} segundos")

    # Iniciar o cronômetro para get_active_users_with_session_start_formatted
    start_time = time.time()
    usuarios_ativos = get_active_users_with_session_start_formatted()
    logger.info(f"get_active_users_with_session_start_formatted executado em {time.time() - start_time} segundos")

    # Iniciar o cronômetro para products_stock_alert
    start_time = time.time()
    alerta_estoque = products_stock_alert()
    logger.info(f"products_stock_alert executado em {time.time() - start_time} segundos")

    # print('meses', meses)
    # print('vendas', vendas)
    # print('meses_cadastro_numero_de_usuarioos', usuarios_cadastrados)
    # print('meses_cadastro', meses_cadastro)
    #
    # print('vendas', vendas)

    context = {
    'quantidade_de_vendas': quantidade_de_vendas,
    'alertas_estoque': alerta_estoque,
    'produtos_mais_vendidos': produtos_mais_vendidos,
    'usuarios_ativos': usuarios_ativos,
    'meses_cadastro': meses_cadastro,
    'usuarios_cadastrados': usuarios_cadastrados,
    'vendas_mensais': vendas_mensais,
    'meses': meses,
    'vendas': vendas,
    }

    return render(request, 'dashboard_admin/home/index.html',context)

def home(request):


    posts = Post.objects.all()[:3]
    hero_banners = HeroBanner.objects.first()
    secondary_banners = SecondaryBanner.objects.all()
    produtos = Product.objects.all()
    produtos = product_with_stock_filter(produtos)
    # Buscar 10 produtos marcados como destaque
    featured_products = produtos.filter(is_featured=True)[:10]
    # Buscar os últimos 10 produtos criados
    latest_products = produtos.order_by('-create_at')[:10]
    # Buscar 10 produtos com mais vendidos
    best_sellers_products = produtos.order_by('-sells')[:3]
    # Buscar 10 produtos com mais avaliações
    review_products = produtos[:10]  # Similar para 'Review'

    context = {

    'hero_banners': hero_banners,
    'secondary_banners': secondary_banners,
    'posts': posts,
    'best_sellers_products': best_sellers_products,
    'latest_products': latest_products,
    'featured_products': featured_products,
    'review_products': review_products,
    }
    return render(request, 'index2.html', context)


def search_view (request, q):
    print(request.GET)
    sort_by = request.GET.get('sort', 'default')
    query = q
    if query:


        base_query = Product.objects.filter(name__icontains=query)
        products_with_stock = product_with_stock_order(base_query)
        base_query= products_with_stock
        # Usar anotação para adicionar o menor preço da variação ou o preço do produto se não houver variação
        print('base_query',base_query)
        annotated_query = base_query.annotate(
            lowest_price=Coalesce(
                # Primeiro, tenta pegar o menor preço promocional das variações, se a promoção estiver ativa
                Min(
                    Case(
                        When(
                            promotion_active=True,
                            then='variations__promotional_price'
                        ),
                        default='variations__price',
                        output_field=DecimalField(max_digits=10, decimal_places=2)
                    )
                ),
                # Se não houver variações, verifica se há um preço promocional no produto
                Case(
                    When(
                        promotion_active=True,
                        then='promotional_price'
                    ),
                    default='price',
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                ),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )

        if sort_by == 'price_asc':
            products = annotated_query.order_by('lowest_price')
        elif sort_by == 'price_desc':
            products = annotated_query.order_by('-lowest_price')
        elif sort_by == 'name_asc':
            products = base_query.order_by('name')  # Adicione mais condições conforme necessário

        elif sort_by == 'name_desc':
            products = base_query.order_by('-name')  # Adicione mais condições conforme necessário
        elif sort_by == 'categoria_acs':
            products = base_query.order_by('category__name')  # Adicione mais condições conforme necessário
        elif sort_by == 'categoria_desc':
            products = base_query.order_by('-category__name')  # Adicione mais condições conforme necessário



        else:
            products = base_query.filter(name__icontains=query)

        # Paginação
        print('products',products)
        page = request.GET.get('page', 1)
        paginator = Paginator(products, 12)  # 10 produtos por página
        total_products = products.count
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        context = {
            'pagina': 'Busca',
            'total_products': total_products,
            'products': products,
        }

        return render(request, 'shop-grid.html', context)






def search(request, q):

    query = q
    print('query',query)
    print('q',q)
    if query:
        products = Product.objects.filter(name__icontains=query)
        print('products',products)
        products_with_stock = product_with_stock_order(products)
        products_limitado = products_with_stock[:5]
        produtos_restantes = products_with_stock.count() - products_limitado.count()
        if produtos_restantes > 0:
            produtos_restantes = f' +{produtos_restantes} produtos'
        else:
            produtos_restantes = ''


        if products.exists():
            # HTML da barra de pesquisa
            search_bar_html = render_to_string('partials/search_bar.html', {'products_count': products.count()}, request)
            # HTML dos produtos
            products_html = ''.join([render_to_string('partials/_product_item_search.html', {'produto': product}, request) for product in products_limitado])
            products_html = f"<div class='products-search'>{products_html}</div>"
            search_bar_footer_html = render_to_string('partials/search_bar_footer.html', {'products_count': produtos_restantes}, request)
            # Combina os dois
            rendered_html = search_bar_html + products_html + search_bar_footer_html
        else:
            # Mensagem quando não há produtos encontrados
            rendered_html = '<div class="no-results">Sem resultados</div>'
    else:
        # Mensagem padrão ou conteúdo vazio se não houver consulta
        rendered_html = '<div class="no-results">Digite algo para buscar</div>'

    return JsonResponse({'html': rendered_html})


def department_detail(request, slug):
    sort_by = request.GET.get('sort', 'default')
    products_desconto = Product.objects.filter(departamento__slug=slug, promotional_price__isnull=False,
                                               promotion_active=True)
    departamento = Department.objects.get(slug=slug)
    base_query = Product.objects.filter(departamento__slug=slug)
    products_with_stock = product_with_stock_order(base_query)
    # Usar anotação para adicionar o menor preço da variação ou o preço do produto se não houver variação

    base_query= products_with_stock
    annotated_query = base_query.annotate(
        lowest_price=Coalesce(
            # Primeiro, tenta pegar o menor preço promocional das variações, se a promoção estiver ativa
            Min(
                Case(
                    When(
                        promotion_active=True,
                        then='variations__promotional_price'
                    ),
                    default='variations__price',
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            ),
            # Se não houver variações, verifica se há um preço promocional no produto
            Case(
                When(
                    promotion_active=True,
                    then='promotional_price'
                ),
                default='price',
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )

    if sort_by == 'price_asc':
        products = annotated_query.order_by('lowest_price')
    elif sort_by == 'price_desc':
        products = annotated_query.order_by('-lowest_price')
    elif sort_by == 'name_asc':
        products = base_query.order_by('name')   # Adicione mais condições conforme necessário

    elif sort_by == 'name_desc':
        products = base_query.order_by('-name')   # Adicione mais condições conforme necessário
    elif sort_by == 'categoria_acs':
        products = base_query.order_by('category__name')  # Adicione mais condições conforme necessário
    elif sort_by == 'categoria_desc':
        products = base_query.order_by('-category__name')  # Adicione mais condições conforme necessário



    else:
        products = base_query.filter(departamento__slug=slug)

    # Paginação

    page = request.GET.get('page', 1)
    paginator = Paginator(products, 12)  # 10 produtos por página
    total_products = products.count
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'pagina': departamento,
        'total_products': total_products,
        'departamento':departamento,
        'products': products,
        'products_desconto': products_desconto,
    }

    return render(request, 'shop-grid.html', context)


def category_detail(request, slug):
    sort_by = request.GET.get('sort', 'default')
    products_desconto = Product.objects.filter(category__slug=slug, promotional_price__isnull=False,
                                               promotion_active=True)

    base_query = Product.objects.filter(category__slug=slug)
    base_query = product_with_stock_order(base_query)
    category = Category.objects.get(slug=slug)

    annotated_query = base_query.annotate(
        lowest_price=Coalesce(
            # Primeiro, tenta pegar o menor preço promocional das variações, se a promoção estiver ativa
            Min(
                Case(
                    When(
                        promotion_active=True,
                        then='variations__promotional_price'
                    ),
                    default='variations__price',
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            ),
            # Se não houver variações, verifica se há um preço promocional no produto
            Case(
                When(
                    promotion_active=True,
                    then='promotional_price'
                ),
                default='price',
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    )

    if sort_by == 'price_asc':
        products = annotated_query.order_by('lowest_price')
    elif sort_by == 'price_desc':
        products = annotated_query.order_by('-lowest_price')
    elif sort_by == 'name_asc':
        products = Product.objects.filter(category__slug=slug).order_by('name')   # Adicione mais condições conforme necessário

    elif sort_by == 'name_desc':
        products = Product.objects.filter(category__slug=slug).order_by('-name')   # Adicione mais condições conforme necessário
    elif sort_by == 'categoria_acs':
        products = Product.objects.filter(category__slug=slug).order_by('category__name')  # Adicione mais condições conforme necessário
    elif sort_by == 'categoria_desc':
        products = Product.objects.filter(category__slug=slug).order_by('-category__name')  # Adicione mais condições conforme necessário



    else:
        products = base_query.filter(category__slug=slug)

    # Paginação

    page = request.GET.get('page', 1)
    paginator = Paginator(products, 12)  # 10 produtos por página
    total_products = products.count
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'pagina': category,
        'total_products': total_products,
        'category':category,
        'products': products,
        'products_desconto': products_desconto,
    }

    return render(request, 'shop-grid.html', context)






