from django.contrib.auth.models import User
from django.http import HttpResponse
from django.db import transaction
import pandas as pd
import io
from django.shortcuts import render
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from datetime import datetime

from products.models import Product, ProductVariation


def upload_csv(request):
    if request.method == "POST":
        csv_file = request.FILES['file']

        if not csv_file.name.endswith('.csv'):
            return HttpResponse("O arquivo não é um CSV.")

        df = pd.read_csv(csv_file)
        error_log = []

        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    username = row['username'].replace(" ", "")
                    validation_result = validate_user_data(row)
                    if validation_result != "OK":
                        raise ValueError(validation_result)  # Levanta um erro com a mensagem específica



                    user, created = User.objects.get_or_create(id=row['id'])
                    user.username = username
                    user.first_name = row['first_name']
                    user.last_name = row['last_name']
                    user.email = row['email']
                    user.is_staff = row.get('is_staff', False)  # Assume False se não definido
                    user.is_active = row.get('is_active', True)  # Assume True se não definido
                    user.date_joined = parse_date(row['date_joined'])
                    user.last_login = parse_date(row['last_login'])
                    if created:
                        user.password = row['password']
                    user.save()
                    print(user)
            except Exception as e:
                error_log.append(f"Erro no registro {index} (Usuário: {row.get('username', 'Não Definido')}): {str(e)}")

        response_message = "Importação concluída com sucesso."
        if error_log:
            response_message += f" Alguns erros foram encontrados: {error_log}"

        return HttpResponse(response_message)
    return render(request, "importador/importador.html")

def validate_user_data(row):
    try:
        validate_email(row['email'])
    except ValidationError:
        return "E-mail inválido."

    if not row['id']:
        return "ID está vazio."

    if not re.match(r"\d{4}-\d{2}-\d{2}", str(row['date_joined'])):
        return "Formato de data_joined inválido."


    return "OK"  # Retorna "OK" se todos os testes passarem

from django.utils import timezone

def parse_date(date_string):
    if pd.isna(date_string) or date_string == '':
        return None  # Retorna None para datas vazias ou nulas
    try:
        naive_datetime = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S.%f')
        return timezone.make_aware(naive_datetime)
    except (ValueError, TypeError):
        return None  # Retorna None se a conversão falhar

from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.db import transaction
import pandas as pd
from usuario.models import UserProfile
from django.shortcuts import render
from datetime import datetime
import json


def upload_csv_for_userprofile(request):
    if request.method == "POST":

        csv_file = request.FILES['file']

        if not csv_file.name.endswith('.csv'):
            return HttpResponse("O arquivo não é um CSV.")

        df = pd.read_csv(csv_file)
        error_log = []
        success_count = 0

        for index, row in df.iterrows():
            print(f"Processando registro {index}...")
            try:
                with transaction.atomic():
                    # Checando se o cpf é NaN e atribuindo None se for
                    if pd.isna(row['cpf']):
                        cpf = None
                    else:
                       cpf = row['cpf']
                    user = User.objects.get(id=row['user_id'])

                    profile, created = UserProfile.objects.get_or_create(id=row['id'], user=user)
                    profile.cpf = cpf

                    # Usa a função format_phone_number para formatar o número de telefone


                    try:
                        phone_number = format_phone_number(row['celular'])
                    except ValueError as ve:
                        error_log.append(f"Registro {index}: Erro de telefone - {ve}")
                        phone_number = None

                    profile.phone_number =phone_number
                    profile.whatsapp = phone_number


                    profile.newsletter = row.get('propaganda', True) == '1'  # Supondo que '1' é True e '0' é False


                    profile.save()
                    print(f"UserProfile salvo: {profile.user.username} (ID: {profile.id}) {profile.user.email}")
                    success_count += 1


            except User.DoesNotExist:

                error = f"Registro {index}: Usuário com ID '{row['user_id']}' não encontrado."

                print(error)

                error_log.append(error)

            except ValueError as ve:
                # Agora registramos o erro de telefone inválido em vez de lançar uma exceção
                error_log.append(f"Registro {index}: Erro de telefone - {ve}")

            except json.JSONDecodeError as jde:
                # Tratamento de erro para campos JSON malformados
                error_log.append(f"Registro {index}: Erro de JSON - {jde}")


            except Exception as e:

                error = f"Registro {index}: Erro inesperado - {str(e)}"

                print(error)

                error_log.append(error)

            response_message = f"Importação concluída. {success_count} perfis salvos com sucesso."



        response_message = f"Importação concluída. {success_count} perfis salvos com sucesso."
        if error_log:
            # Agora adicionamos detalhes dos erros
            response_message += f" Foram encontrados erros em {len(error_log)} registros: {error_log}"

        return HttpResponse(response_message)

    return render(request, "importador/importador_usuario.html")


def parse_date_userprofile(date_string):
    if pd.isna(date_string) or date_string.strip() == '':
        return None
    try:
        return datetime.strptime(date_string.strip(), '%Y-%m-%d %H:%M:%S.%f')
    except (ValueError, TypeError):
        return None

import re


def format_phone_number(phone_string):
    if pd.isna(phone_string) or phone_string.strip() == '':
        return None

    # Remove caracteres especiais mantendo apenas os números
    phone_number = re.sub(r'\D', '', phone_string)

    # Adicione aqui qualquer validação de número de telefone que você desejar
    # Por exemplo, verificar o comprimento do número:
    if len(phone_number) < 10 or len(phone_number) > 11:
        raise ValueError(f"Número de telefone inválido: {phone_number}")


    return phone_number



# Caminho: /path/to/your/django/project/views.py

# Supondo que UserProfile, Session e Address sejam modelos Django importados corretamente.
from django.shortcuts import render
from django.http import HttpResponse
from django.db import transaction
import pandas as pd
from usuario.models import Address, UserProfile, Session

def upload_csv_for_address(request):
    if request.method == "POST":
        csv_file = request.FILES['file']

        if not csv_file.name.endswith('.csv'):
            return HttpResponse("O arquivo não é um CSV.")

        df = pd.read_csv(csv_file)
        error_log = []
        success_count = 0

        for index, row in df.iterrows():
            if pd.isna(row['cliente_id']):
                error = f"Registro {index}: ID do cliente está vazio."
                print(error)
                error_log.append(error)
                continue
            else:
                cliente_id = int(row['cliente_id'])

            print(f"Processando registro {index}...cliente_id: {cliente_id}")
            try:
                with transaction.atomic():
                    try:
                        cliente_id= int(row['cliente_id'])
                        cliente = UserProfile.objects.get(id=cliente_id)
                        print(f"Cliente encontrado: {cliente.user.get_full_name()}")

                    except UserProfile.DoesNotExist:
                        error = f"Registro {index}: UserProfile com ID '{cliente_id}' não encontrado."
                        print(error)
                        error_log.append(error)
                        continue
                    # Criação ou atualização do endereço
                    address, created = Address.objects.get_or_create(
                        user_profile_id=cliente_id)
                    address.destinatario = cliente.user.get_full_name()
                    address.cpf_destinatario = cliente.cpf
                    address.rua = row['rua']
                    address.numero = row['numero']
                    address.bairro = row['bairro']
                    address.cidade = row['cidade']
                    address.complemento = row['complemento'] if pd.notna(row['complemento']) else None
                    address.estado = row['estado']

                    cep_raw = str(row['cep'])
                    address.cep = cep_raw.zfill(9)
                    address.pais = 'Brasil'


                    address.is_primary = True if row['primario'] == 1.0 else False

                    address.save()
                    print(f"Endereço salvo: {address.destinatario}, {address.cidade}")
                    success_count += 1

            except Exception as e:
                error = f"Registro {index}: Erro inesperado - {str(e)}"
                print(error)
                error_log.append(error)

        response_message = f"Importação concluída. {success_count} endereços salvos com sucesso."
        if error_log:
            response_message += f" Foram encontrados erros em {len(error_log)} registros: {error_log}"

        return HttpResponse(response_message)

    return render(request, "importador/importador_endereco.html")

# Funções auxiliares, como formatação de telefone, podem ser adicionadas conforme necessário.
# Este código assume que os IDs de UserProfile e Session são fornecidos no CSV.
# Adapte conforme a necessidade do seu modelo de dados e regras de negócio.


from django.shortcuts import render
from django.http import HttpResponse
from django.db import transaction
import pandas as pd
from usuario.models import UserProfile
from pedidos.models import Order, OrderItem  # Substitua 'seu_app' pelo nome do seu app Django
from django.db import transaction, IntegrityError

def upload_csv_for_orders(request):
    if request.method != "POST":
        return render(request, "importador/importador_pedidos.html")

    csv_file = request.FILES.get('file')
    if not csv_file or not csv_file.name.endswith('.csv'):
        return HttpResponse("O arquivo não é um CSV.")

    df = pd.read_csv(csv_file)
    error_log = []
    success_count = 0

    for index, row in df.iterrows():
        if pd.isna(row['user_id']):
            error_log.append(f"Registro {index}: ID do usuário está vazio.")
            continue

        try:
            with transaction.atomic():
                user = User.objects.get(id=row['user_id'])
                user_profile = UserProfile.objects.get(user=user)
                order, created = Order.objects.get_or_create(id=row['id'], user_profile=user_profile)

                # Mapeamento dos campos
                order.created_at = parse_date(row['data_pedido'])
                order.updated_at = parse_date(row['data_atualizacao'])
                order.total = row['total']
                order.status = row['status']
                order.tipo_frete = row['frete']
                order.valor_frete = row['valor_frete']
                order.payment_method = row['metodo_de_pagamento']
                order.subtotal = row['subtotal']
                order.coupon = row['cupom_id']
                order.discount = row['desconto']
                order.destinatario = user.get_full_name()
                order.email_pedido = user.email
                order.cpf_destinatario = user_profile.cpf
                order.rua = row['rua']
                order.numero = row['numero']
                order.bairro = row['bairro']
                order.cidade = row['cidade']
                order.complemento = row.get('complemento', '')
                order.estado = row['estado']
                order.cep = row['cep']
                order.id_tiny = row['numero_pedido_tiny']
                order.mercadopago_link = row['link_mercado_pago']
                order.mercado_pago_id = row['mercado_pago_id']
                order.rastreio = None if pd.isna(row['rastreamento']) else row['rastreamento']
                order.em_producao = row['producao']
                order.observacoes = None if pd.isna(row['observacoes']) else row['observacoes']
                order.is_primary = True if row['status'] == 'Enviado' or row['status'] == 'pago' or  row['status'] == 'Pago' else False
                order.save()
                success_count += 1


        except IntegrityError as e:

            error_log.append(f"Registro {index}: Erro de integridade - {str(e)}")

        except User.DoesNotExist:

            error_log.append(f"Registro {index}: Usuário não encontrado.")

        except Exception as e:  # Para outros erros inesperados

            error_log.append(f"Registro {index}: Erro inesperado - {str(e)}")

        response_message = f"Importação concluída. {success_count} pedidos salvos com sucesso. "

        if error_log:
            response_message += f"Erros encontrados em {len(error_log)} registros: {error_log}"

    return HttpResponse(response_message)

    return render(request, "importador/importador_pedidos.html")


from django.shortcuts import render
from django.http import HttpResponse
from django.db import transaction
import pandas as pd
from usuario.models import UserProfile
from pedidos.models import Order  # Substitua 'seu_app' pelo nome do seu app Django
from django.db import transaction, IntegrityError

import pandas as pd
from django.db import transaction, IntegrityError
from pedidos.models import Order, OrderItem
from products.models import Product, ProductVariation

def upload_csv_for_order_items(csv_filepath):
    df = pd.read_csv(csv_filepath)
    error_log = []
    success_count = 0

    for index, row in df.iterrows():
        if pd.isna(row['id']):
            error_log.append(f"Registro {index}: ID do usuário está vazio.")
            continue

        try:
            with transaction.atomic():
                print(f"Processando registro {index}...")
                pedido = Order.objects.get(id=row['pedido_id'])
                print(f"Pedido encontrado: {pedido.id}")
                print(f"Produto ID: {int(row['product_id'])}")
                produto = Product.objects.get(external_id=int(row['product_id']))
                print(f"Variation Id: {int(row['variation_id'])}")
                variation = ProductVariation.objects.get(id=int(row['variation_id'])) if not pd.isna(row['variacao_id']) else None
                print(f"Produto encontrado para pedido {pedido}: {produto.name} - {variation.name if variation else ''}")
                item, created = OrderItem.objects.get_or_create(
                    id=row['pedidoitem_id'], product=produto,
                    order=pedido, quantity=row['quantidade'],
                    price=row['preco'], variation=variation
                )
                if created:
                    print(f"Item criado: {item.product.name} - {item.quantity}")

                success_count += 1

        except IntegrityError as e:
            error_log.append(f"Registro {index}: Erro de integridade - {str(e)}")
        except Order.DoesNotExist:
            error_log.append(f"Registro {index}: Pedido não encontrado.")
        except Product.DoesNotExist:
            error_log.append(f"Registro {index}: Produto não encontrado.")
        except Exception as e:  # Para outros erros inesperados
            error_log.append(f"Registro {index}: Erro inesperado - {str(e)}")

    response_message = f"Importação concluída. {success_count} pedidos salvos com sucesso. "
    if error_log:
        response_message += f"Erros encontrados em {len(error_log)} registros: {error_log}"
    return response_message