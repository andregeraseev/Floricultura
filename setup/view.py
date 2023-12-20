from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from products.models import Product, Department, Category, ProductVariation, ProductMaterial
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from banners.models import HeroBanner, SecondaryBanner
from blog.models import Post
from django.db.models import Case, When, Value, F, Min, DecimalField
from django.db.models.functions import Coalesce
from django.db.models import Case, When, Value, BooleanField, F, Q, Exists, OuterRef


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


def search_view (request):
    print(request.GET)
    sort_by = request.GET.get('sort', 'default')
    query = request.GET.get('q', '')
    if query:


        base_query = Product.objects.filter(name__icontains=query)
        products_with_stock = product_with_stock_order(base_query)
        base_query= products_with_stock
        # Usar anotação para adicionar o menor preço da variação ou o preço do produto se não houver variação

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






def search(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query)
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



