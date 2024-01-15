import time

from rest_framework import serializers
from products.models import (
    Product, Category, Department, ProductImage,
    ProductVariation, MateriaPrima, ProductVariationRawMaterial
)
from django.core.files.base import ContentFile
from rest_framework.exceptions import APIException
import requests
import logging
from setup.settings import TINY_API_TOKEN
logger = logging.getLogger('webhookstiny')

TINY_API_TOKEN = TINY_API_TOKEN

TINY_API_URL = "https://api.tiny.com.br/api2/"
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ['category', 'departamento', 'slug']

    def to_internal_value(self, data):
        """
        Converte os nomes dos campos recebidos da API externa para os nomes dos campos do modelo.
        """
        try:
            logger.info(f"data: {data}")
            data['price'] = data.pop('preco', None)
            print('data',data['price'])
            data['name'] = data.pop('nome', None)

            data['description'] = data.pop('descricaoComplementar', None)
            # Garantir que pesoLiquido e pesoBruto tenham no máximo duas casas decimais
            data['pesoLiquido'] = round(float(data.get('pesoLiquido', 0)), 2)
            data['pesoBruto'] = round(float(data.get('pesoBruto', 0)), 2)
            data['unidadePorCaixa'] = 1
            return super().to_internal_value(data)
        except Exception as e:
            logger.error(f"Erro ao converter os dados: {e}")
            raise APIException("Erro ao converter os dados")

    def create(self, validated_data):
        """
        Cria um novo produto ou atualiza um existente.
        """

        # Verificar se o produto é matéria-prima
        if validated_data.get('classeProduto') == 'M':
            try:
                logger.info(f"Criando Materia prima: {validated_data}")
                # Tratar como matéria-prima
                return self.handle_materia_prima(validated_data)
            except Exception as e:
                logger.error(f"Erro ao criar matéria-prima: {e}")
                raise APIException(f"Erro ao criar matéria-prima: {e}")
        try:
            logger.info(f"Obejto recebido: {validated_data}")
            arvore_categorias = self.context.get("request").get('arvoreCategoria', [])
            print('arvore_categorias',arvore_categorias)
            departamento, categoria = self.process_departamento_e_categoria(arvore_categorias)

            validated_data['category'] = categoria
            validated_data['departamento'] = departamento
            validated_data['skuMapeamento'] = validated_data['codigo']
            payload = self.context.get("request", {})
            id = payload.get('id')
            product, _ = Product.objects.update_or_create(
                external_id=id,
                defaults=validated_data
            )

            self.process_images(product, self.context['request'].get('anexos', []))
            self.process_variacoes(product, self.context.get("request").get('variacoes', []))

            return product
        except Exception as e:
            logger.error(f"Erro ao criar/atualizar o produto: {e}")

    def process_departamento_e_categoria(self, arvore_categorias):
        """
        Processa o departamento e as categorias a partir da árvore de categorias.
        """
        departamento = None
        categoria = None
        try:
            if arvore_categorias:
                departamento_data = arvore_categorias[0]
                departamento, _ = Department.objects.get_or_create(
                    id=departamento_data['id'],
                    defaults={'name': departamento_data['descricao']}
                )
                for categoria_data in arvore_categorias:
                    categoria, _ = Category.objects.get_or_create(
                        id=categoria_data['id'],
                        defaults={
                            'name': categoria_data['descricao'],
                            'department': departamento,
                            'id_pai': categoria_data['idPai']
                        }
                    )
                return departamento, categoria
        except Exception as e:
            logger.error(f"Erro ao processar departamento e categoria: {e}")
            return None, None


    def process_images(self, product, anexos):
        """
        Processa e salva as imagens anexadas ao produto, evitando duplicatas.
        """
        try:
            for anexo in anexos:
                url_imagem = anexo.get('url', '')
                nome_imagem = anexo.get('nome', '')
                if url_imagem and nome_imagem:
                    try:
                        resposta = requests.get(url_imagem)
                        if resposta.status_code == 200:
                            # Verificar se já existe uma imagem com o mesmo nome
                            existing_image = ProductImage.objects.filter(product=product,
                                                                         image__endswith=nome_imagem).first()
                            if existing_image:
                                # Substitui a imagem existente
                                existing_image.image.delete(save=False)  # Deleta a imagem antiga
                                existing_image.image.save(nome_imagem, ContentFile(resposta.content), save=True)
                            else:
                                # Cria uma nova imagem
                                product_image = ProductImage(product=product)
                                product_image.image.save(nome_imagem, ContentFile(resposta.content), save=True)
                    except requests.RequestException as e:
                        logger.error(f"Erro ao processar imagem: {e}")
        except Exception as e:
            logger.error(f"Erro ao processar imagens: {e}")

    def process_variacoes(self, product, variacoes_data):
        """
        Processa as variações do produto, incluindo a matéria-prima relacionada.
        """
        for variacao_data in variacoes_data:
            logger.info(f"Variacao recebida: {variacao_data}")

            try:
                variacao, _ = ProductVariation.objects.update_or_create(
                    external_id=variacao_data['id'],
                    defaults=self.get_variation_defaults(variacao_data, product)
                )
                logger.info(f"Variação processada com sucesso: {variacao.id}")
            except Exception as e:
                logger.error(
                    f"Erro ao processar variações: {e}, Variação ID: {variacao_data.get('idMapeamento')}, Produto ID: {product.id}")

            try:
                self.process_kit(variacao)
            except Exception as e:
                logger.error(f"Erro ao processar kit: {e}, Variação ID: {variacao_data.get('idMapeamento')}, Produto ID: {product.id}")
    def get_variation_defaults(self, variacao_data, product):
        """
        Retorna os valores padrão para criar/atualizar uma variação de produto.
        """
        return {
            'id': variacao_data['id'],
            'external_id': variacao_data['id'],
            # 'nome': variacao_data['nome'],
            'idMapeamento': variacao_data['idMapeamento'],
            'product': product,
            'skuMapeamento': variacao_data['codigo'],
            'codigo': variacao_data['codigo'],
            'gtin': variacao_data['gtin'],
            'price': variacao_data['preco'],
            'promotional_price': variacao_data['precoPromocional'],
            'estoqueAtual': variacao_data['estoqueAtual'],
            'grade': variacao_data['grade'],
        }

    def process_kit(self, variacao):
        url = f"{TINY_API_URL}produto.obter.php?token={TINY_API_TOKEN}&id={variacao.id}&formato=json"
        try:
            response = self.make_tiny_api_request(url)
            if response['status'] != 'OK':

                logger.debug(f"Resposta da API: {response}")

                if any(erro.get('erro') == 'API Bloqueada - Excedido o número de acessos a API' for erro in
                       response.get('erros', [])):
                    logger.info("API rate limit exceeded, waiting for 1 minute")
                    time.sleep(60)
                    response = self.make_tiny_api_request(url)
                    if response['status'] != 'OK':
                        logger.error(f"Erro ao processar kit: {response}")
                        raise APIException(f"Erro na API Tiny: {response}")
                else:

                    logger.debug(f"Erros da API: {response.get('erros', [])}")
                    logger.error(f"Erro ao processar kit: {response}")
                    raise APIException(f"Erro na API Tiny: {response}")



            try:
                logger.info(f"variacao obtida: {response['produto']}")
                variacao.nome = response['produto']['nome']
                variacao.save()
            except Exception as e:
                logger.error(f"Erro ao processar kit: {e}")
                raise APIException("Erro ao obter variacao")

            if response['produto']['classe_produto'] == 'K':

                for item in response['produto']['kit']:
                    try:
                        rawmaterial = self.processar_materia_prima(variacao, item)
                    except Exception as e:
                        logger.error(f"Erro ao processar matéria-prima: {e}")
                        raise APIException("Erro ao processar matéria-prima")


                    try:
                        if rawmaterial:
                            self.processar_item_kit(variacao, item, rawmaterial)
                    except Exception as e:
                        logger.error(f"Erro ao processar item do kit: {e}")
                        raise APIException("Erro ao processar item do kit")
            else:
                print('Nenhum kit encontrado',response['produto'])
                logger.info(f"Nenhum kit encontrado para a variação: {variacao.id}")
        except requests.RequestException as e:
            logger.error(f"Erro na requisição à API Tiny: {e}")
            raise APIException("Erro de comunicação com a API Tiny")

    def make_tiny_api_request(self, url):
        """
        Faz uma requisição à API do Tiny e retorna a resposta processada.
        """
        try:
            headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
            response = requests.post(url, headers=headers)
            return response.json()['retorno']
        except requests.RequestException as e:
            logger.error(f"Erro na requisição à API Tiny: {e}")
            raise APIException("Erro de comunicação com a API Tiny")


    def processar_materia_prima(self, variacao, item_kit):
        raw_material_id = item_kit['item']['id_produto']
        url = f"{TINY_API_URL}produto.obter.estoque.php?token={TINY_API_TOKEN}&id={raw_material_id}&formato=json"
        try:
            response = self.make_tiny_api_request(url)
            if response['status'] != 'OK':

                logger.debug(f"Resposta da API: {response}")
                # Check for the specific API blocked error
                if any(erro.get('erro') == 'API Bloqueada - Excedido o número de acessos a API' for erro in
                       response.get('erros', [])):
                    logger.info("API rate limit exceeded, waiting for 1 minute")
                    time.sleep(60)
                    response = self.make_tiny_api_request(url)
                    if response['status'] != 'OK':
                        logger.error(f"Erro ao processar kit: {response}")
                        raise APIException(f"Erro na API Tiny: {response}")
                else:
                    logger.debug(f"Erros da API: {response.get('erros', [])}")
                    logger.error(f"Erro ao processar kit: {response}")
                    raise APIException(f"Erro na API Tiny: {response}")
            if 'saldo' in response['produto']:
                print('Materia prima',response['produto'])
                try:
                    raw_material, _ = MateriaPrima.objects.get_or_create(
                        name=response['produto']['nome'],
                        defaults={'external_id':response['produto']['id'], 'name': response['produto']['nome'], 'stock': response['produto']['saldo']}
                    )
                    logger.info(f"Materia prima criada com sucesso: {raw_material.id}")
                    return raw_material
                except Exception as e:
                    logger.error(f"Erro ao processar matéria-prima: {e}")
                    raise APIException("Erro ao processar matéria-prima")
            else:
                print('Nenhum kit encontrado', response['produto'])
                logger.info(f"Nenhum kit encontrado para a variação: {raw_material_id}")
                return None
        except requests.RequestException as e:
            logger.error(f"Erro na requisição à API Tiny: {e}")
            raise APIException("Erro de comunicação com a API Tiny")

    def handle_materia_prima(self, validated_data):
        logger.info(f"Criando Handle Materia Prima: {validated_data}")
        try:
            payload = self.context.get("request", {})
            id = payload.get('id')
            print('id',id)
            # Verificar se 'id' é válido e existe

            if id is not None and MateriaPrima.objects.filter(external_id=id).exists():
                print('material prima existe')
                try:
                    # Atualizar o registro existente
                    materia_prima = MateriaPrima.objects.get(external_id=id)
                    print('materia_prima',materia_prima)

                    materia_prima.idMapeamento = validated_data['idMapeamento']
                    materia_prima.name = validated_data['name']
                    materia_prima.stock = validated_data['estoqueAtual']
                    materia_prima.skuMapeamento = validated_data['codigo']
                    materia_prima.save()
                    created = False
                except Exception as e:
                    logger.error(f"Erro ao atualizar matéria-primaBBBBB: {e}")
                    raise APIException(f"Erro ao atualizar matéria-prima: {e}")
            else:
                try:
                    print('material prima nao existe')
                    # Criar um novo registro
                    materia_prima = MateriaPrima.objects.create(

                        external_id=id,
                        idMapeamento=validated_data['idMapeamento'],
                        name=validated_data['name'],
                        stock=validated_data['estoqueAtual'],
                        skuMapeamento=validated_data['codigo']
                    )
                    created = True
                except Exception as e:
                    logger.error(f"Erro ao criar matéria-prima: {e}")
                    raise APIException(f"Erro ao criar matéria-primaAAAAA{e}")
            if created:
                logger.info(f"Materia prima criada com sucesso: {materia_prima.id}")
            else:
                logger.info(f"Materia prima atualizada com sucesso: {materia_prima.id}")

            return materia_prima
        except Exception as e:
            logger.error(f"Erro ao criar/atualizar a matéria-prima: {e}")
            raise APIException(f"Erro ao criar/atualizar a matéria-prima {e}")

    def processar_item_kit(self, variacao, item_kit, raw_material):
        """
        Processa um item individual do kit, atualizando ou criando a matéria-prima correspondente.
        """

        try:
            quantity_used = item_kit['item']['quantidade']

            ProductVariationRawMaterial.objects.update_or_create(
                product_variation=variacao,
                materia_prima=raw_material,
                defaults={'quantity_used': quantity_used}
            )
            logger.info(f"Item do kit processado: {variacao.id} - {raw_material.name}")
        except Exception as e:
            logger.error(f"Erro ao processar item do kit: {e}")
            raise APIException("Erro ao processar item do kit")





