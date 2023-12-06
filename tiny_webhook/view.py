from rest_framework.views import APIView
from rest_framework.response import Response
from tiny_webhook.serializers import ProductSerializer

class ProductWebhook(APIView):
    def post(self, request, format=None):
        print(request.data.dados)
        serializer = ProductSerializer(data=request.data.dados, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)
