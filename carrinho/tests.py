from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta
from carrinho.models import ShoppingCart, UserProfile, Product, ProductVariation, Category
from products.models import    Department

class ShoppingCartModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Cria um usuário
        user = User.objects.create_user(username='testuser', password='password')

        # Supondo que UserProfile tem um campo relacionado 'user'
        cls.user_profile = UserProfile.objects.create(user=user)

        # Cria uma sessão com data de expiração
        expire_date = timezone.now() + timedelta(days=1)
        cls.session = Session.objects.create(session_key='testsession', expire_date=expire_date)

        # Criação de objetos Department e Category se necessário
        department = Department.objects.create(name='Test Department')
        category = Category.objects.create(name='Test Category', department=department)

        # Criação de objetos Product e ProductVariation
        cls.product = Product.objects.create(
            name='Test Product',
            price=10.0,
            departamento=department,
            category=category
        )
        cls.variation = ProductVariation.objects.create(
            product=cls.product,
            price=8.0,
            estoqueAtual=100
        )

        # Criação de ShoppingCart
        cls.cart = ShoppingCart.objects.create(user_profile=cls.user_profile, session=cls.session)

    # Demais métodos de teste...



    def test_str_representation(self):
        self.assertEqual(str(self.cart), f"Carrinho de {self.user_profile.user.username if self.user_profile else 'Anonymous'} 'ID' {self.user_profile.id if self.user_profile else 'Anonymous'} Cart ID{self.cart.id}")



    def test_cart_total(self):
        # Adicionando um produto ao carrinho para teste
        self.cart.items.create( product=self.product, variation=self.variation, quantity=5)
        expected_total = sum(item.total_price_or_promotional_price for item in self.cart.items.all())
        self.assertEqual(self.cart.total, expected_total)

    def test_verifica_estoque_suficiente_para_adicao(self):
        # Teste com quantidade suficiente
        result = self.cart.verifica_estoque_suficiente_para_adicao(self.product, self.variation, 1)
        self.assertTrue(result)

        # Teste com quantidade insuficiente
        with self.assertRaises(Exception) as context:
            self.cart.verifica_estoque_suficiente_para_adicao(self.product, self.variation, 222)
            self.assertTrue('Estoque insuficiente para o produto' in str(context.exception))

    # Adicione testes adicionais para outros métodos conforme necessário


