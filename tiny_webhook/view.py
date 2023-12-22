from django.http import HttpResponse
from products.models import Product
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

            idmapeamento = serializer.data['idMapeamento']
            skumapeamento = serializer.data['skuMapeamento']
            mapeamentos = [
                {"idMapeamento": idmapeamento,
                "skuMapeamento": skumapeamento,}
            ]


            produto = Product.objects.get(skuMapeamento=skumapeamento)

            for variation in produto.variations.all():
                skumapeamento = variation.skuMapeamento
                idmapeamento = variation.idMapeamento
                mapeamentos.append({"idMapeamento": idmapeamento,
                "skuMapeamento": skumapeamento,})

            print("MAPEAMENTO",serializer.data['idMapeamento'],serializer.data['skuMapeamento'])



            return HttpResponse(json.dumps(mapeamentos), content_type="application/json", status=200)
        else:
            return HttpResponse(serializer.errors, content_type="application/json", status=400)
