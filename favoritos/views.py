from django.http import JsonResponse
from django.views import View
from products.models import Product
from.models import WishlistItem
import json
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

