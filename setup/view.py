from django.shortcuts import render

from products.models import Product, Department, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Min
from django.db.models.functions import Coalesce



def home(request):
    return render(request, 'index2.html')



def department_detail(request, slug):
    sort_by = request.GET.get('sort', 'default')
    products_desconto = Product.objects.filter(departamento__slug=slug, promotional_price__isnull=False,
                                               promotion_active=True)
    departamento = Department.objects.get(slug=slug)
    base_query = Product.objects.filter(departamento__slug=slug)

    # Usar anotação para adicionar o menor preço da variação ou o preço do produto se não houver variação
    from django.db.models import Case, When, Value, F, Min, DecimalField
    from django.db.models.functions import Coalesce

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
        products = Product.objects.filter(departamento__slug=slug).order_by('name')
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
    category = Category.objects.get(slug=slug)
    if sort_by == 'price_asc':
        products = Product.objects.filter(category__slug=slug).order_by('price')

    elif sort_by == 'price_desc':
        products = Product.objects.filter(category__slug=slug).order_by('-price')
    elif sort_by == 'name_asc':
        products = Product.objects.filter(category__slug=slug).order_by('name')   # Adicione mais condições conforme necessário

    elif sort_by == 'name_desc':
        products = Product.objects.filter(category__slug=slug).order_by('-name')   # Adicione mais condições conforme necessário
    elif sort_by == 'categoria_acs':
        products = Product.objects.filter(category__slug=slug).order_by('category__name')  # Adicione mais condições conforme necessário
    elif sort_by == 'categoria_desc':
        products = Product.objects.filter(category__slug=slug).order_by('-category__name')  # Adicione mais condições conforme necessário



    else:
        products = Product.objects.filter(category__slug=slug).order_by('name')
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
        'total_products': total_products,
        'category':category,
        'products': products,
        'products_desconto': products_desconto,
    }

    return render(request, 'shop-grid.html', context)



