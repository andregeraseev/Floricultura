# meuapp/management/commands/enviar_avisos_reestoque.py
from django.core.management.base import BaseCommand
from avise.views import envia_avisos_reestoque  # Importe sua função aqui

class Command(BaseCommand):
    help = 'Envia e-mails para usuários sobre o reestoque de produtos'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando o processo de envio de avisos de reestoque...")
        try:
            envia_avisos_reestoque()
            self.stdout.write(self.style.SUCCESS("Avisos de reestoque enviados com sucesso."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erro ao enviar avisos de reestoque: {e}"))
