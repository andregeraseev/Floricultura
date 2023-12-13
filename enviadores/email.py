from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from setup.settings import EMAIL_HOST_USER



def enviar_email_confirmacao(destinatario, nome):
    assunto = 'Confirmação de Cadastro'
    # mensagem = f'Olá {nome}, \n\nObrigado por se cadastrar no nosso site. Seu cadastro foi confirmado com sucesso!'
    remetente = EMAIL_HOST_USER

    # Define o conteúdo do e-mail em HTML e texto puro
    html_content = render_to_string('emails/Bem_vindo.html', {'nome': nome})
    text_content = strip_tags(html_content)

    # Cria a mensagem
    msg = EmailMultiAlternatives(assunto, text_content, remetente, [destinatario])
    msg.attach_alternative(html_content, "text/html")

    # Envia o e-mail
    msg.send()

    # send_mail(assunto, html_content, remetente, [destinatario], fail_silently=False)


def enviar_email_pedido_criado(destinatario, nome, order ):
    print('enviado email')
    assunto = 'Pedido Criado'
    mensagem = f'Olá {nome}, \n\nSeu pedido #{order} foi criado com sucesso.'
    remetente = EMAIL_HOST_USER
    # send_mail(assunto, mensagem, remetente, [destinatario], fail_silently=False)

    # Define o conteúdo do e-mail em HTML e texto puro
    html_content = render_to_string('emails/pedido2.html', {'nome': nome,'order':order })
    text_content = strip_tags(html_content)

    # Cria a mensagem
    msg = EmailMultiAlternatives(assunto, text_content, remetente, [destinatario])
    msg.attach_alternative(html_content, "text/html")

    # Envia o e-mail
    msg.send()

def enviar_email_rastreio(destinatario, nome, pedido_id, rastreio):
    print('enviado email rastreio')
    assunto = 'Pedido Enviado'
    mensagem = f'Olá {nome}, \n\nSeu pedido #{pedido_id} foi criado com sucesso.'
    remetente = EMAIL_HOST_USER
    # send_mail(assunto, mensagem, remetente, [destinatario], fail_silently=False)

    # Define o conteúdo do e-mail em HTML e texto puro
    html_content = render_to_string('emails/rastreio.html', {'nome': nome,'pedido_id':pedido_id, "rastreio": rastreio })
    text_content = strip_tags(html_content)

    # Cria a mensagem
    msg = EmailMultiAlternatives(assunto, text_content, remetente, [destinatario])
    msg.attach_alternative(html_content, "text/html")

    # Envia o e-mail
    msg.send()



def send_email_aviso_estoque(aviso):

    assunto = 'Produto em estoque'
    message = f"Olá {aviso.cliente.username}, o produto {aviso.produto.name} está em estoque novamente!"
    remetente = EMAIL_HOST_USER
    destinatario = [aviso.cliente.email]
    # send_mail(subject, message, from_email, recipient_list)

    html_content = render_to_string('emails/aviso_reestoque.html',
                                    {'aviso': aviso,})
    text_content = strip_tags(html_content)

    # Cria a mensagem
    msg = EmailMultiAlternatives(assunto, text_content, remetente, destinatario)
    msg.attach_alternative(html_content, "text/html")

    # Envia o e-mail
    msg.send()

