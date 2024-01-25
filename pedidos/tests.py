from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from pedidos.views import mudar_endereco
from usuario.models import Address
from django.core.exceptions import ObjectDoesNotExist
import json

class MudarEnderecoTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.address = Address.objects.create(id=1, is_primary=False)

    def test_mudar_endereco_success(self):
        request = self.factory.post('/mudar_endereco', json.dumps({'endereco_id': 1}), content_type='application/json')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        response = mudar_endereco(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertEqual(response.json()['message'], 'Endereço atualizado Address object (1) com sucesso')
        self.address.refresh_from_db()
        self.assertEqual(self.address.is_primary, True)

    def test_mudar_endereco_address_does_not_exist(self):
        request = self.factory.post('/mudar_endereco', json.dumps({'endereco_id': 2}), content_type='application/json')
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        response = mudar_endereco(request)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['success'], False)
        self.assertEqual(response.json()['error'], 'Endereço não encontrado')

    def test_mudar_endereco_exception(self):
        with self.assertRaises(ObjectDoesNotExist):
            request = self.factory.post('/mudar_endereco', json.dumps({'endereco_id': 'invalid'}), content_type='application/json')
            middleware = SessionMiddleware()
            middleware.process_request(request)
            request.session.save()
            mudar_endereco(request)