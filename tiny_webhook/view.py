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

        serializer = ProductSerializer(data=payload['dados'], context={'request': payload['dados']})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)
