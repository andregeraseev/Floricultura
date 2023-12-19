# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import mercadopago
import os
import logging
from setup.settings import MERCADOPAGOTOLKEN
logger = logging.getLogger(__name__)
from setup.settings import SITE
def cria_preferencia(request,total, id_pedido):
    try:

        if not total or not id_pedido:
            logger.error("Dados faltando: total ou id_pedido")
            return Response({"error": "Dados faltando"}, status=status.HTTP_400_BAD_REQUEST)
        print(total)
        print(id_pedido)
        sdk = mercadopago.SDK(MERCADOPAGOTOLKEN)
        preference_data = {
            'items': [
                {'currency_id': 'BRL', 'description': 'pagamento XF', 'title': 'Produto XF',
                 'quantity': 1, 'unit_price': float(total)}],
            "back_urls": {
                "success": f"{SITE}/pedidos/mercadopago/success",
                "failure": f"{SITE}/pedidos/mercadopago/failure",
                "pending": f"{SITE}pedidos/mercadopago/pending"
            },
            'redirect_urls': {
                "success": f"{SITE}/pedidos/mercadopago/success",
                "failure": f"{SITE}/pedidos/mercadopago/failure",
                "pending": f"{SITE}pedidos/mercadopago/pending"
            },
            "external_reference": id_pedido,
            "auto_return": "approved",

        }

        preference_response = sdk.preference().create(preference_data)
        print('preference_response',preference_response)
        if preference_response['status'] != 201:
            raise Exception(f"Erro na criação da preferência: {preference_response}")

        preference = preference_response["response"]
        print(preference['init_point'])
        return preference['init_point']

    except Exception as e:
        logger.error(f"Erro ao criar preferência: {e}")
        return Response({"error": "Erro interno do servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)