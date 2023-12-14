from django.http import JsonResponse
from django.views import View
from products.models import Product
from.models import WishlistItem
import json
from django.shortcuts import render

from products.models import Product, Department, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db.models import Case, When, Value, F, Min, DecimalField
from django.db.models.functions import Coalesce


class FavoritosView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            pagina = 'favoritos'
            sort_by = request.GET.get('sort', 'default')

            base_query = Product.objects.filter(wishlistitem__user_profile=request.user.profile)

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
                products = Product.objects.filter(wishlistitem__user_profile=request.user.profile).order_by('name')
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
                'pagina': pagina,
                'total_products': total_products,
                'favoritos': 'favorito',
                'products': products,

            }

            return render(request, 'shop-grid.html', context)

class AdicionarFavoritoView(View):




    def favorite_counter(self, request):
        if request.user.is_authenticated:
            return request.user.profile.wishlist.count()
        else:
            return 0

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        produto_id = data.get('produto_id')
        try:
            favorito, create = WishlistItem.objects.get_or_create(user_profile=request.user.profile, product=Product.objects.get(id=produto_id))
            if create:
                favorite_counter = self.favorite_counter(request)
                return JsonResponse({'success':'true' ,'message': favorito.success_message, 'favorite_counter': favorite_counter})
            else:
                 favorito.delete()
                 favorite_counter = self.favorite_counter(request)
                 return JsonResponse({'success':'true' ,'message': favorito.delete_message, 'favorite_counter': favorite_counter})

        except WishlistItem.DoesNotExist:
            return JsonResponse({'success':'false' ,'message': favorito.error_message})
        except Exception as e:
            return JsonResponse({'success':'false' ,'message': e})

