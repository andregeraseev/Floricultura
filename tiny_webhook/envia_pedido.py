import requests
import json
from setup.settings import TINY_API_TOKEN
def enviar_pedido_para_tiny(order):
    url = 'https://api.tiny.com.br/api2/pedido.incluir.php'
    token = TINY_API_TOKEN

    # Montando os dados do pedido
    pedido_data = {
        'pedido': {
            'data_pedido': order.created_at.strftime('%d/%m/%Y'),
            'cliente': {
                'nome': order.destinatario,
                'tipo_pessoa': 'F' if len(order.cpf_destinatario) == 11 else 'J',
                'cpf_cnpj': order.cpf_destinatario,
                'endereco': order.rua,
                'numero': order.numero,
                'bairro': order.bairro,
                'cep': order.cep,
                'cidade': order.cidade,
                'uf': order.estado,
                'fone': '',  # Adicionar campo de telefone se disponível
                'email': order.email_pedido,
            },
            'itens': [{
                'item': {
                    'codigo': item.product_or_variation.codigo,
                    'descricao': item.product_or_variation.name,
                    'unidade': 'UN',
                    'quantidade': item.quantity,
                    'valor_unitario': str(item.price)
                }
            } for item in order.items.all()],
            # Adicionar outros campos conforme necessário
        }
    }

    # Enviando o pedido para o Tiny
    try:
        response = requests.post(url, data={'token': token, 'formato': 'json', 'pedido': json.dumps(pedido_data)})
    except Exception as e:
        print('ERRO REQUEST', e)
        return {'erro': 'Falha ao enviar pedido para o Tiny'}, None
    try:
        if response.status_code == 200:
            print(response.json())
            reponse_json= response.json()
            id_pedido = reponse_json['retorno']['registros']['registro']['numero']
            print('idpeidido',id_pedido)
            return f"{order.id }Pedido enviado com sucesso para o tiny como pedido {id_pedido}", int(id_pedido)
        else:
            # Tratar erro
            return {'erro': 'Falha ao enviar pedido para o Tiny'}, None
    except Exception as e:
        print('ERRO RESPONSE', e)
        return {'erro': 'Falha ao enviar pedido para o Tiny'}, None
