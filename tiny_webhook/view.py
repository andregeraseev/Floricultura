from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from tiny_webhook.serializers import ProductSerializer
import json

def parse_payload(request_body):
    try:
        return json.loads(request_body.decode("utf-8"))
    except json.JSONDecodeError:
        return None

class ProductWebhook(APIView):
    def post(self, request, format=None):
        payload = parse_payload(request.body)
        print('payload',payload)
        serializer = ProductSerializer(data=payload['dados'], context={'request': payload['dados']})
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            # Construir a resposta esperada pelo Tiny
            print("MAPEAMENTO",serializer.data['idMapeamento'],serializer.data['skuMapeamento'])
            mapeamentos = {
                "idMapeamento": serializer.data['idMapeamento'],
                "skuMapeamento": serializer.data['skuMapeamento'],

            }


            return HttpResponse(json.dumps(mapeamentos), content_type="application/json", status=200)
        else:
            return HttpResponse(serializer.errors, content_type="application/json", status=400)
