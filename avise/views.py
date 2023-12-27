from avise.models import AviseItem
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from enviadores.email import send_email_aviso_estoque
from products.models import Product
import json
import logging

log = logging.getLogger(__name__)

class AviseView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'avise.html', {})

    def post(self, request, *args, **kwargs):
        try:
            if request.user.is_anonymous:
                return JsonResponse({'error': 'Voce precisa estar cadastrado para adicinar alertas de reestoque'}, status=400)

            else:
                user_profile = request.user.profile
                data = json.loads(request.body)
                produto_id = data.get('produto_id')
                produto= Product.objects.get(id=produto_id)
                avisar, create = AviseItem.objects.get_or_create(user_profile=user_profile, product=produto, email_sent=False)
                if create:
                    return JsonResponse({'success': True, 'message': f'produto {produto.name} adicionado a sua lista de aviso'
                                                                     f' de reestoque' }, status=200)
                else:
                    return JsonResponse({'error': f'Voce ja esta cadastrado para receber alertas de reestoque do produto {produto.name}'}, status=400)


        except Product.DoesNotExist:
            return JsonResponse({'error': 'Produto não encontrado'}, status=400)

    def delete(self, request, *args, **kwargs):
        try:
            if request.user.is_anonymous:
                return JsonResponse({'error': 'Voce precisa estar cadastrado para adicinar alertas de reestoque'}, status=400)

            else:
                user_profile = request.user.profile
                data = json.loads(request.body)
                produto_id = data.get('produto_id')
                produto = Product.objects.get(id=produto_id)
                avisar = AviseItem.objects.get(user_profile=user_profile, product=produto)
                avisar.delete()
                return JsonResponse({'success': True, 'message': f'produto {produto.name} removido da sua lista de aviso'
                                                                 f' de reestoque'}, status=200)

        except Product.DoesNotExist:
            return JsonResponse({'error': 'Produto não encontrado'}, status=400)

from django.utils import timezone


def envia_avisos_reestoque():
    print('enviando avisos de reestoque')
    avisos = AviseItem.objects.filter(email_sent=False)
    count = 0

    for aviso in avisos:
        print(aviso.product.has_stock)
        try:
            if aviso.product.has_stock:
                print('enviando email')
                aviso.email_sent = True
                aviso.email_sent_on = timezone.now()
                aviso.save()
                try:
                    send_email_aviso_estoque(aviso)
                    count += 1
                    log.info(f'enviado email de aviso de reestoque para {aviso.user_profile.user.email}')
                except Exception as e:
                    log.error(f'erro ao enviar email de aviso de reestoque para {aviso.user_profile.user.email} - {e}')
            else:
                pass
        except Exception as e:
            log.error(f'erro avise: {e}')
    print(f'{count} email de avisos enviados')