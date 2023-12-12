from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date
from django.contrib.auth.models import User
# from favoritos.models import WishlistItem
# from products.models import Product
from django.contrib.sessions.models import Session


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    cpf = models.CharField(max_length=14, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    whatsapp = models.CharField(max_length=15, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], blank=True, null=True)
    newsletter = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Preferências e Comportamento de Compra
    purchase_history = models.JSONField(blank=True, null=True)
    product_preferences = models.JSONField(blank=True, null=True)


    # Interações com o Site
    browsing_history = models.JSONField(blank=True, null=True)
    marketing_responses = models.JSONField(blank=True, null=True)
    customer_service_interactions = models.JSONField(blank=True, null=True)

    # Dados Demográficos Adicionais (Opcionais)
    income_range = models.CharField(max_length=50, blank=True, null=True)
    education_level = models.CharField(max_length=50, blank=True, null=True)

    # Programa de Fidelidade e Recompensas
    loyalty_points = models.IntegerField(default=0)
    reward_status = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return self.user.username


    # Em UserProfile
    def add_to_wishlist(self, product_id):
        from products.models import Product
        from favoritos.models import WishlistItem
        product = Product.objects.get(id=product_id)
        WishlistItem.objects.get_or_create(user_profile=self, product=product)

    # Em UserProfile
    def remove_from_wishlist(self, product_id):
        from products.models import Product
        from favoritos.models import WishlistItem
        product = Product.objects.get(id=product_id)
        WishlistItem.objects.filter(user_profile=self, product=product).delete()

    # Em UserProfile
    def is_product_in_wishlist(self, product_id):
        from favoritos.models import WishlistItem
        return WishlistItem.objects.filter(user_profile=self, product__id=product_id).exists()

    # Em UserProfile
    def get_wishlist_items(self):
        return self.wishlist.all()

    # Em UserProfile
    def clear_wishlist(self):
        self.wishlist.all().delete()

    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                        (today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None

    def add_loyalty_points(self, points):
        self.loyalty_points += points
        self.save()

    def remove_loyalty_points(self, points):
        self.loyalty_points -= points
        self.save()

    @property
    def primary_address(self):
        return self.addresses.filter(is_primary=True).first()

    def get_cart(self, request):
        from carrinho.models import ShoppingCart

        session = Session.objects.get(session_key=request.session.session_key)
        session_cart= ShoppingCart.objects.get_or_create(user_profile=self,
                                           session=session)
        return session_cart
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

class Address(models.Model):
    ESTADOS_BRASIL = [
                  ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
                  ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
                  ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
                  ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
                  ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
                  ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
                  ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
              ]


    user_profile = models.ForeignKey(UserProfile, related_name='addresses', on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey(Session, related_name='session_addresses', on_delete=models.CASCADE, null=True, blank=True)
    destinatario = models.CharField(max_length=50)
    cpf_destinatario = models.CharField(max_length=14,null=True, blank=True)
    rua = models.CharField(max_length=50)
    numero = models.CharField(max_length=5)
    bairro = models.CharField(max_length=30)
    cidade = models.CharField(max_length=50)
    complemento = models.CharField(max_length=30, blank=True, null=True)
    estado = models.CharField(choices=ESTADOS_BRASIL, max_length=2)
    cep = models.CharField(max_length=9)
    pais = models.CharField(max_length=50, default='Brasil')
    is_primary = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Verifica se existe um user_profile associado
        if self.user_profile:
            # Se o endereço atual deve ser o primário
            if self.is_primary:
                # Define todos os outros endereços do mesmo perfil como não primários
                self.user_profile.addresses.filter(is_primary=True).update(is_primary=False)
        else:
            # Se não houver um user_profile, verifica se este é o primeiro endereço a ser salvo
            # Se for, define-o como primário por padrão
            if not self.__class__.objects.exists():
                self.is_primary = True

        super().save(*args, **kwargs)

    @property
    def toggle_primary(self):
        self.is_primary = not self.is_primary
        self.save()

    @property
    def full_address(self):
        return f"{self.rua}, {self.cidade}, {self.estado}, {self.cep}, {self.pais}"

    def __str__(self):
        return f"{self.rua}, {self.cidade}, {self.estado}, {self.cep}, {self.pais}"

    def get_wishlist_items(self):
        return self.wishlist.all()
    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')




class UserLoginHistory(models.Model):
    user_profile = models.ForeignKey(UserProfile, related_name='login_history', on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_profile.user.username} logged in from {self.ip_address} on {self.login_time}"

    @property
    def time_since_login(self):
        return timezone.now() - self.login_time

    class Meta:
        verbose_name = _('user login history')
        verbose_name_plural = _('user login histories')







class UserPageVisit(models.Model):
    user_profile = models.ForeignKey(UserProfile, related_name='page_visits', on_delete=models.CASCADE)
    url = models.URLField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user_profile.user.username} visited {self.url} on {self.timestamp}"

    class Meta:
        verbose_name = _('user page visit')
        verbose_name_plural = _('user page visits')




