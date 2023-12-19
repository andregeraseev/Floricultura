# SeuProjeto/views.py
import os
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import mercadopago
import json
# from tiny_erp.envia_pedido import enviar_pedido_para_tiny
from pedidos.models import Order
import logging
logger = logging.getLogger('pedidos')
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import mercadopago
import os
import json
import logging
from setup.settings import MERCADOPAGOTOLKEN
logger = logging.getLogger('webhookspagamento')

class MercadoPagoWebhook(APIView):
    def post(self,request, *args, **kwargs):
        try:
            if request.data:
                data = request.data
                logger.info("data.", data)

        except Exception as e:
            logger.error(f"Erro ao processar o webhook: {e} {request.POST}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        data = request.data
        resource_type = data.get('type')
        resource_id = data.get('data', {}).get('id')

        if not resource_type or not resource_id:
            logger.error("Campos requeridos estão faltando.")
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sdk = mercadopago.SDK(MERCADOPAGOTOLKEN)

            resource_type = data['type']
            print('resource_type', resource_type)
            resource_id = data['data']['id']

            print('resource_id',resource_id)
            if resource_type == 'payment':
                try:
                    result = sdk.payment().get(resource_id)

                except Exception as e:
                    logger.error(f"Erro ao buscar o pagamento: {e}")
                    return JsonResponse({'error': 'Erro ao buscar o pagamento'}, status=500)

                if result['status'] == 200:
                    payment = result['response']
                    print('payment', payment)
                    logger.info(f"Referencias MercadoPago: {payment}")

                    # Obtenha a external_reference da resposta
                    external_reference = payment.get("external_reference")
                    print("ID do pedido", external_reference)

                    # Atualize o status do Pedido com base no status do pagamento
                    payment_status = payment['status']
                    try:
                        pedido = Order.objects.get(id=external_reference)
                        pedido.mercado_pago_id = resource_id

                        status_map = {
                            'approved': 'Pago',
                            'pending': 'Pendente',
                            'authorized': 'Autorizado',
                            'in_process': 'Em Análise',
                            'in_mediation': 'Em Mediação',
                            'rejected': 'Rejeitado',
                            'cancelled': 'Cancelado',
                            'refunded': 'Reembolsado',
                            'charged_back': 'Estornado',
                            'failed': 'Falha no Pagamento'

                        }

                        pedido.status = status_map.get(payment_status, 'Status não reconhecido')
                        pedido.save()
                        if payment_status == 'approved' and pedido.status != 'Pago':
                            pedido.status = 'Pago'
                            # enviar_pedido_para_tiny(pedido)
                            print(external_reference, 'PEDIDO, STATUS MUDADO PARA PAGO')



                        else:
                            print(f"Status de pagamento não reconhecido: {payment_status}")

                    except Order.DoesNotExist:
                        logger.error(f"Pedido não encontrado: {external_reference}")
                        return HttpResponse(status=404)

            elif resource_type == 'plan':
                plan = sdk.plan().get(resource_id)
                print('plan',plan)
            elif resource_type == 'subscription':
                subscription = sdk.subscription().get(resource_id)

            elif resource_type == 'point_integration_wh':
                # data contains the information related to the notification
                pass
            else:
                logger.error(f"Tipo de recurso inválido: {resource_type}")
                return Response({'error': 'Invalid resource type.'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'success': 'Notification received and processed.'}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro no processamento do webhook: {e}")
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)