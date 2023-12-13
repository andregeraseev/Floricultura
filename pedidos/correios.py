
from carrinho.models import ShoppingCart, ShoppingCartItem
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import requests
import re
import base64
import logging
from setup.settings import USUARIO_CORREIOS, SENHA_COREIOS



logger = logging.getLogger(__name__)
def obter_novo_token_correios_com_cartao():
    url = "https://api.correios.com.br/token/v1/autentica/cartaopostagem"

    # Seus dados de autenticação
    # ATENÇÃO: Substitua 'SEU_USUARIO' e 'SUA_SENHA' pelos seus dados reais
    usuario = USUARIO_CORREIOS
    senha = SENHA_COREIOS
    credentials = base64.b64encode(f"{usuario}:{senha}".encode()).decode()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {credentials}'
    }

    # Dados do cartão de postagem
    payload = {
        "numero": "0068060211"  # Altere para o número do seu cartão se necessário
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Verifica se a requisição foi bem-sucedida

        data = response.json()
        return data["token"]

    except requests.RequestException as e:
        # Log ou trate o erro conforme necessário
        print(f"Erro ao obter novo token dos Correios: {e}")
        return None

def cotacao_frete_correios(request, cart, adress):
    """
    Obtém cotações de frete dos Correios para o endereço do cliente.

    Com base nos itens no carrinho do cliente, esta função faz uma requisição
    aos Correios para obter cotações de frete para o endereço do cliente.

    Parameters:
    - request: objeto HttpRequest contendo o CEP do endereço de entrega.

    Returns:
    - JsonResponse com os resultados da cotação ou uma mensagem de erro.
    """
    print('cotacao_frete_correios')

    print('cart')
    itens = cart.items.all()

    # Calcula o peso dos itens do carrinho caso o peso for menor que 300 gramas o total peso fica igual a 300 gramas
    total_peso = 0
    print('itens')
    try:
        for item in itens:
            peso = item.product.pesoBruto
            total_peso += item.quantity * peso
        if total_peso < 0.3:
            total_peso = 0.3
    except:
        logger.warning(f"Problemas para calcular peso do carrinho {cart}, do usuario ")
        total_peso = 0.3

    # Definindo as informações para a consulta
    print('adress')
    cep_origem = '12233400'
    cep_destino = adress.cep
    if cep_destino is None:
        logger.error('Erro ao coletar cep do destinatario ')
        return JsonResponse({'error': 'Tivemos um erro com cep, verifique por gentileza'})
    # Removendo qualquer caractere que não seja dígito
    cep_destino = re.sub(r'\D', '', cep_destino)

    # Aqui estamos definindo o token para autorização
    Token_Api_Correios = obter_novo_token_correios_com_cartao()
    print(Token_Api_Correios)
    token = Token_Api_Correios
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json'
    }

    servicos = ["03220", "03298"]
    results = []

    try:
        for servico in servicos:
            base_url = f"https://api.correios.com.br"

            # Parâmetros comuns para ambas as requisições
            params = {
                "cepOrigem": cep_origem,
                "cepDestino": cep_destino,
                "psObjeto": total_peso,
                "tpObjeto": 2,
                "comprimento": 20,
                "largura": 20,
                "altura": 20
            }

            # Obtendo o prazo de entrega
            url_prazo = f"{base_url}/prazo/v1/nacional/{servico}"
            response_prazo = requests.get(url_prazo, headers=headers, params=params)

            # Obtendo o preço
            url_preco = f"{base_url}/preco/v1/nacional/{servico}"
            response_preco = requests.get(url_preco, headers=headers, params=params)

            # Se a resposta de qualquer uma das requisições não for bem-sucedida, registre e retorne o erro
            if response_prazo.status_code != 200:
                error_msg = response_prazo.json().get("msgs", "Erro desconhecido ao obter prazo.")
                if error_msg == ['PRZ-101: O valor do(s) parâmetro(s) cepDestino é(são) inválido(s). ']:
                    error_msg = "Por gentileza confira o CEP, o campo CEP precisa de ter 8 digitos numericos."

                if error_msg == ['PRZ-101: O valor do(s) parâmetro(s) cepDestino é(são) inválido(s). ']:
                    error_msg = "Por gentileza confira o CEP, o campo CEP precisa de ter 8 digitos numericos."
                logger.error(
                    f"Erro ao obter prazo para o serviço do usuario  {servico}: {error_msg}")
                return JsonResponse({'error': f'Tivemos um problema ao obter o prazo de entrega: \n{error_msg}'})

            if response_preco.status_code != 200:
                error_msg = response_preco.json().get("msgs", "Erro desconhecido ao obter preço.")
                logger.error(f"Erro ao obter preço para o serviço : {servico}: {error_msg}")
                return JsonResponse({'error': f'Tivemos um problema ao obter o preço. {error_msg}'})

            # Processando dados
            data_prazo = response_prazo.json()
            data_preco = response_preco.json()

            nome_servico = 'SEDEX' if servico == '03220' else 'PAC' if servico == '03298' else 'Outro'

            days = int(data_prazo["prazoEntrega"])
            prazo_entrega = f"{days} {'dia útil' if days == 1 else 'dias úteis'}"
            results.append({
                'codigo': nome_servico,
                'valor': data_preco["pcFinal"].replace(',', '.'),
                'prazodeentrega': prazo_entrega
            })

        logger.info(f'Usuário  finalizou cotação de frete. {results}')
        return JsonResponse({'results': results})

    except Exception as e:
        logger.error('Erro ao cotar frete dos Correios para o usuário %s. Erro: %s', str(e))
        return JsonResponse({'error': 'Tivemos um erro ao cotar o frete. Por favor, recarregue o frete.'})