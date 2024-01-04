from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
from products.models import MateriaPrima, Product,ProductVariation
import logging
logger = logging.getLogger('webhookstiny')

@csrf_exempt
def tiny_webhook_stock_update(request):
    logger.info("Informação de estoque recebida do TinyERP")
    # Verifica se a solicitação é um POST
    if request.method != "POST":
        logger.error("Esse endpoint suporta somente requisições POST")
        return HttpResponseBadRequest("Esse endpoint suporta somente requisições POST")

    # Lê o corpo da solicitação e decodifica o JSON
    try:
        payload = json.loads(request.body.decode("utf-8"))
        logger.info(f"payload: {payload}")
    except json.JSONDecodeError:
        logger.error("Falha ao decodificar JSON")
        return HttpResponseBadRequest("Falha ao decodificar JSON")

    # Processa o evento de atualização de estoque

    if payload['tipo'] == 'estoque':
        logger.info(f'ATUALIZANDO ESTOQUE{payload}')
        print('Estoque',payload)
        try:
            estoque = payload['dados']
            logger.info(f"Estoque payload: {estoque}")
            # id_mapeamento = estoque['idMapeamento']
            # print(id_mapeamento)
            estoque_atual = estoque['saldo']
            logger.info(f"Estoque atual:{estoque_atual}")
            id_produto = estoque['idProduto']
            logger.info(f"Id produto: {id_produto}")





            # Tenta atualizar a MateriaPrima
            try:
                materia_prima = MateriaPrima.objects.get(id=id_produto)
                logger.info(f"Materia prima:{materia_prima}")
                materia_prima.stock = estoque_atual
                logger.info(f"Estoque atual:{estoque_atual}")
                materia_prima.save()
                logger.info(f"Materia prima salva com novo estoque :{materia_prima}")
            except MateriaPrima.DoesNotExist:
                logger.info("Materia prima não encontrada")
                try:
                    logger.info(f"Produto:{id_produto}")
                    produto = Product.objects.get(id=id_produto)
                    produto.stock = estoque_atual
                    produto.save()
                    logger.info(f"Produto salvo com estoque novo: {produto}")

                except Product.DoesNotExist:
                    logger.info("Produto não encontrado")

                    try:
                        product_variation = ProductVariation.objects.get(id=id_produto)
                        product_variation.stock = estoque_atual
                        product_variation.save()
                        logger.info(f"Produto variação salva com novo estoque :{product_variation}")
                    except ProductVariation.DoesNotExist:
                        logger.info("Produto variação não encontrado")
                        logger.error("Nenhum produto encontrado para atualizar estoque")
                        return HttpResponse(status=200)

            # Retorna uma resposta de sucesso
            return HttpResponse(status=200)

            # Retorna uma resposta de sucesso
            return HttpResponse(status=200)

        except Exception as e:
            logger.error(f"Erro ao processar evento de atualização de estoque: {e}")
            return HttpResponseBadRequest("Erro ao processar evento de atualização de estoque: {}".format(str(e)))

    else:
        logger.error("Tipo de evento desconhecido")
        return HttpResponseBadRequest("Tipo de evento desconhecido")