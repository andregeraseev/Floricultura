from django.db import models
from django.core.exceptions import ValidationError
from colorfield.fields import ColorField

class SiteSettings(models.Model):
    # Informações Básicas
    active = models.BooleanField(default=False)
    site_name = models.CharField(max_length=100, default='Meu Site')
    logo = models.ImageField(upload_to='settings/', blank=True, null=True)
    favicon = models.ImageField(upload_to='settings/', blank=True, null=True)

    # Informações de Contato
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)

    # SEO
    seo_description = models.TextField(blank=True)
    seo_keywords = models.TextField(blank=True)

    # Mídias Sociais
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    # Google Analytics
    google_analytics_id = models.CharField(max_length=20, blank=True)

    # Configurações de E-mail
    email_host = models.CharField(max_length=100, blank=True)
    email_port = models.IntegerField(default=587)
    email_host_user = models.CharField(max_length=100, blank=True)
    email_host_password = models.CharField(max_length=100, blank=True)
    use_tls = models.BooleanField(default=True)

    # Rodapé e Mensagens Legais
    footer_text = models.TextField(blank=True)
    terms_of_service_url = models.URLField(blank=True)
    privacy_policy_url = models.URLField(blank=True)

    # Configurações de Pagamento
    payment_api_key = models.CharField(max_length=100, blank=True)

    # Personalização de Tema
    theme_color = models.CharField(max_length=7, default='#000000')  # Exemplo: '#FF5733'
    theme_font = models.CharField(max_length=50, default='Arial')

    # Pesonlização do Navbar
    menu_lateral =models.BooleanField(default=False)
    header = ColorField(max_length=7, default='#f5f5f5')  # Para cor
    header_secundario = ColorField(max_length=7, default='#FFFFFF')  # Para cor
    mobili_header_secundario = ColorField(max_length=7, default='#FFFFFF')  # Para cor
    navbar_color = ColorField(max_length=7, default='#FFFFFF')  # Para cor
    navbar_icons = ColorField(max_length=7, default='#FFFFFF')  # Para cor
    navbar_icons_circle_background = ColorField(max_length=7, default='#dc3545')  # Para cor
    navbar_icons_circle_text = ColorField(max_length=7, default='#FFFFFF')  # Para cor
    mobile_navbar_icons = ColorField(max_length=7, default='#FFFFFF')  # Para cor
    mobile_navbar_icons_circle_background = ColorField(max_length=7, default='#dc3545')  # Para cor
    mobile_navbar_icons_circle_text = ColorField(max_length=7, default='#FFFFFF')  # Para cor
    footer_background = ColorField(max_length=7, default='#f5f5f5')  # Para cor
    footer_text_color = ColorField(max_length=7, default='#1c1c1c')  # Para cor

    navbar_font = models.CharField(max_length=50, default='Arial')  # Para fonte
    navbar_font_weight = models.CharField(max_length=100, default='normal', choices=(
        ('normal', 'Normal'),
        ('bold', 'Negrito'),
        ('bolder', 'Muito Negrito'),
    ))
    navbar_font_style = models.CharField(max_length=100, default='normal', choices=(
        ('normal', 'Normal'),
        ('italic', 'Itálico'),
    ))
    # Personalização do Banner Principal
    navbar_fixo = models.BooleanField(default=False)

    # Personalização do Banner Principal
    banner_principal =models.BooleanField(default=True)
    # Personalização do Carrocel de Departamentos
    carrocel_departamentos =models.BooleanField(default=True)

    # Personalização do Carrocel de Produtos em destaque
    carrocel_produtos =models.BooleanField(default=True)

    # Persalização de banner secundadrio
    banners_secundarios =models.BooleanField(default=True)

    # Carrocel triplo
    carrocel_triplo =models.BooleanField(default=True)

    # Blog
    blog =models.BooleanField(default=True)



    # Versão do setting
    version_number = models.IntegerField(default=1)



    def save(self, *args, **kwargs):
        # Incrementa o número da versão a cada salvamento
        self.version_number += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Configurações do Site"

    class Meta:
        verbose_name = 'Configuração do Site'


class SocialLink(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField()
    icon_class = models.CharField(max_length=100)

    def __str__(self):
        return self.name



class ContactInfo(models.Model):
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    email = models.EmailField()

    def save(self, *args, **kwargs):
        if ContactInfo.objects.exists() and not self.pk:
            raise ValidationError('Não é possível criar mais de uma instância de ContactInfo.')
        return super(ContactInfo, self).save(*args, **kwargs)

    def __str__(self):
        return "Informações de Contato"

class UsefulLink(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField()
    category = models.CharField(max_length=100, help_text="Categoria para agrupar links")

    def __str__(self):
        return self.title
