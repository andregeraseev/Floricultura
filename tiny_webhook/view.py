from django.http import HttpResponse
from products.models import Product, MateriaPrima
from rest_framework.views import APIView
from rest_framework.response import Response
from tiny_webhook.serializers import ProductSerializer
import json
import logging

logger = logging.getLogger('webhookstiny')


def parse_payload(request_body):
    try:
        logger.info(f'payload {request_body}')
        return json.loads(request_body.decode("utf-8"))
    except json.JSONDecodeError:
        logger.error(f'payload {request_body}')
        return None

class ProductWebhook(APIView):
    def post(self, request, format=None):
        try:
            payload = parse_payload(request.body)
            print('payload',payload)
            serializer = ProductSerializer(data=payload['dados'], context={'request': payload['dados']})
            if serializer.is_valid():
                print('serializer VALIDO')
                try:
                    try:
                        serializer.save()
                        print('serializer SALVO')
                    except Exception as e:
                        print('erro pos-salvar',e)
                    try:
                        idmapeamento = serializer.context['request']['idMapeamento']
                        mapeamentos = []
                    except Exception as e:
                        print('erro mapeamento',e)
                        logger.error(f'postTiny {e}')
                        return HttpResponse(e, content_type="application/json", status=400)


                    try:
                        print('TENTANDO')
                        print('ID',serializer.context['request']['id'])
                        if serializer.context['request']['classeProduto'] == 'M':
                            print('MATERIA PRIMA')
                            try:
                                try:
                                    logger.info(f'Buscando por idMapeamento')
                                    produto = MateriaPrima.objects.get(idMapeamento=idmapeamento)
                                except:
                                    logger.info(f'Não encontrou por idMapeamento, tentando por id')
                                    produto = MateriaPrima.objects.get(id=serializer.context['request']['id'])

                                logger.info(f'produto {produto}')
                            except Exception as e:
                                logger.error(f'postTiny buscando id {e}')
                            try:

                                skumapeamento = produto.skuMapeamento
                                idmapeamento = produto.idMapeamento
                                mapeamentos.append({"idMapeamento": idmapeamento,
                                                    "skuMapeamento": skumapeamento, })

                            except Exception as e:
                                print('erro mapeamento',e)
                                logger.error(f'postTiny {e}')
                                return HttpResponse(e, content_type="application/json", status=400)
                        else:
                            try:
                                try:
                                    produto = Product.objects.get(idMapeamento=idmapeamento)
                                    # print('produto',produto)
                                except:
                                    produto = Product.objects.get(skuMapeamento=serializer.context['request']['codigo'])
                                skumapeamento = produto.skuMapeamento
                                idmapeamento = produto.idMapeamento
                                mapeamentos.append({"idMapeamento": idmapeamento,
                                                    "skuMapeamento": skumapeamento, })
                                if produto.variations.all():
                                    for variation in produto.variations.all():
                                        skumapeamento = variation.skuMapeamento
                                        idmapeamento = variation.idMapeamento
                                        mapeamentos.append({"idMapeamento": idmapeamento,
                                        "skuMapeamento": skumapeamento,})
                            except Exception as e:
                                print('erro variations',e)
                                return HttpResponse(e, content_type="application/json", status=400)

                    except Exception as e:
                        print('erro total',e)
                        logger.error(f'postTiny {e}')
                        return HttpResponse(e, content_type="application/json", status=400)

                except Exception as e:
                    logger.error(f'postTiny {e}')
                    print('erro total2',e)
                    return HttpResponse(e, content_type="application/json", status=400)

                logger.info(f'MAPEAMENTOS {mapeamentos}')
                return HttpResponse(json.dumps(mapeamentos), content_type="application/json", status=200)
            else:
                print('serializer Invalido')

                logger.error(f'postTiny {serializer.errors}')
                return HttpResponse(serializer.errors, content_type="application/json", status=400)
        except Exception as e:
            logger.error(f'postTiny {e}')
            return HttpResponse(e, content_type="application/json", status=400)
