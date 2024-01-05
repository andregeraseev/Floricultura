from django.db import models
from django.utils.text import slugify
from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
import os
from uuid import uuid4
from django.urls import reverse
import json
from django.contrib.auth.models import User


def path_and_rename(instance, filename):
    upload_to = 'product_images'
    return os.path.join(upload_to, filename)
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    promotional_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    promotion_active = models.BooleanField(default=False)
    # image = models.ImageField(upload_to=path_and_rename)
    # image_thumbnail = ImageSpecField(source='image',
    #                                  processors=[ResizeToFill(100, 100)],
    #                                  format='JPEG',
    #                                  options={'quality': 60})
    departamento = models.ForeignKey('Department', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    sells = models.PositiveIntegerField(default=0)


    # Identificação e Informações Básicas
    idMapeamento = models.CharField(max_length=255, blank=True, null=True)
    skuMapeamento = models.CharField(max_length=255, blank=True, null=True)
    codigo = models.CharField(max_length=255,blank=True, null=True)
    unidade = models.CharField(max_length=50,blank=True, null=True)
    ncm = models.CharField(max_length=50, blank=True, null=True)
    origem = models.CharField(max_length=50, blank=True, null=True)
    gtin = models.CharField(max_length=255, blank=True, null=True)
    gtinEmbalagem = models.CharField(max_length=255, blank=True, null=True)

    # Localização e Estoque
    localizacao = models.CharField(max_length=255, blank=True, null=True)
    estoqueMinimo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estoqueMaximo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estoqueAtual = models.IntegerField(default=0)
    sobEncomenda = models.CharField(max_length=1, blank=True, null=True)

    # Informações Adicionais
    obs = models.TextField(blank=True, null=True)
    garantia = models.CharField(max_length=255, blank=True, null=True)
    cest = models.CharField(max_length=255, blank=True, null=True)
    marca = models.CharField(max_length=255, blank=True, null=True)
    classeProduto = models.CharField(max_length=1, blank=True, null=True)
    diasPreparacao = models.CharField(max_length=255, blank=True, null=True)

    # Dimensões e Peso
    alturaEmbalagem = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    larguraEmbalagem = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    comprimentoEmbalagem = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pesoLiquido = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    pesoBruto = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    # Campos adicionais com base no arquivo JSON
    idFornecedor = models.BigIntegerField(blank=True, null=True)
    codigoFornecedor = models.CharField(max_length=255, blank=True, null=True)
    codigoPeloFornecedor = models.CharField(max_length=255, blank=True, null=True)
    unidadePorCaixa = models.IntegerField(blank=True, null=True)
    precoCusto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    precoCustoMedio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    situacao = models.CharField(max_length=1, blank=True, null=True)
    tipoEmbalagem = models.CharField(max_length=255, blank=True, null=True)
    diametroEmbalagem = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    idCategoria = models.BigIntegerField(blank=True, null=True)
    descricaoCategoria = models.CharField(max_length=255, blank=True, null=True)
    descricaoArvoreCategoria = models.TextField(blank=True, null=True)


    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def add_sells(self, quantidade):
        self.sells += quantidade
        self.save()

    @property
    def get_firs_image(self):
        if self.images.first():
            return self.images.first().image_thumbnail.url
        return 'https://via.placeholder.com/100x100'

    @property
    def get_absolute_url(self):
        return reverse('produtos', kwargs={'slug': self.slug})

    def has_variations(self):
        return self.variations.exists()

    @property
    def promocao_ativa(self):
        if self.promotional_price and self.promotion_active:
            return True
        return False

    @property
    def porcentagem_de_desconto(self):
        if self.promotional_price and self.promotion_active:
            return round((1 - (self.promotional_price / self.price)) * 100)
        return 0

    @property
    def price_or_promocional_price(self):
        if self.promotional_price and self.promotion_active:
            return self.promotional_price
        return self.price

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def stock_suficiente(self, quantidade):
        if self.has_stock:
            if self.product_materials.all():
                for material in self.product_materials.all():

                    if material.materia_prima.stock < material.quantity_used * quantidade:
                        return False
                return True
            else:
                if self.estoqueAtual >= quantidade:
                    return True
                return False

    @property
    def has_stock(self):
        if self.variations.all():
            for variation in self.variations.all():
                if variation.has_stock:
                    return True
            return False

        elif self.product_materials.all():
            for material in self.product_materials.all():
                if material.materia_prima.stock < material.quantity_used:
                    return False
            return True
        else:
            if self.estoqueAtual > 0:
                return True
            return False

    @property
    def lista_avise(self):
        from avise.models import AviseItem
        lista_avise = AviseItem.objects.filter(product=self)
        product_in_avise = [product.product_id for product in lista_avise]
        if self.id in product_in_avise:
            return True
        else:
            return False

class ProductVariation(models.Model):
    nome = models.CharField(max_length=255, blank=True, null=True)
    product = models.ForeignKey(Product, related_name='variations', on_delete=models.CASCADE)
    idMapeamento = models.CharField(max_length=255)
    skuMapeamento = models.CharField(max_length=255, blank=True, null=True)
    codigo = models.CharField(max_length=255, blank=True, null=True)
    gtin = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    promotional_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estoqueAtual = models.IntegerField()
    grade = models.TextField()


    def stock_suficiente(self, quantidade):
        if self.has_stock:
            if self.variation_materials.all():
                for material in self.variation_materials.all():
                    if material.materia_prima.stock < material.quantity_used * quantidade:
                        return False
                return True
            else:
                if self.estoqueAtual >= quantidade:
                    return True
                return False

    @property
    def has_stock(self):
        if self.variation_materials.all():
            for material in self.variation_materials.all():
                if material.materia_prima.stock < material.quantity_used:
                    return False
            return True
        else:
            if self.estoqueAtual > 0:
                return True
            return False



    def __str__(self):
        return f"{self.product.name} \n {self.grade_bonita}"

    def set_grade(self, data):
        self.grade = json.dumps(data)

    @property
    def promocao_ativa(self):
        if self.promotional_price and self.product.promotion_active:
            return True
        return False

    @property
    def price_or_promocional_price(self):
        if self.promotional_price and self.product.promotion_active:
            return self.promotional_price
        return self.price




    @property
    def grade_bonita(self):
        grade = json.loads(self.grade.replace("'", '"'))
        grade_bonita = []

        for item in grade:
            chave = item.get('chave', '')
            valor = item.get('valor', '')
            grade_bonita.append(f"{chave}: {valor}")

        return ', '.join(grade_bonita)

    @property
    def name(self):
        return f"{self.product.name} \n {self.grade_bonita}"

    @property
    def porcentagem_de_desconto(self):
        if self.promotional_price:
            return round((1 - (self.promotional_price / self.price)) * 100)
        return 0

    @property
    def get_grade(self):
        return json.loads(self.grade.replace("'", '"'))

    class Meta:
        ordering = ['price']


class MateriaPrima(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    idMapeamento = models.CharField(max_length=255, blank=True, null=True)
    skuMapeamento = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        print('save')



        if self.pk:
            old_stock = MateriaPrima.objects.get(pk=self.pk).stock
        else:
            old_stock = None

        super().save(*args, **kwargs)

        if old_stock is not None and old_stock != self.stock:
            print('update_stock_history')
            update_stock_history(self, old_stock, self.stock)
        else:
            print('not update_stock_history')

class ProductMaterial(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_materials')
    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.CASCADE)
    quantity_used = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.materia_prima.name}"

class ProductVariationRawMaterial(models.Model):
    product_variation = models.ForeignKey(ProductVariation, on_delete=models.CASCADE, related_name='variation_materials')
    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.CASCADE)
    quantity_used = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product_variation.product.name} - {self.materia_prima.name}"



class Department(models.Model):
    name = models.CharField(max_length=100)
    image_department = models.ImageField(upload_to='departamentos/')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def get_absolute_url(self):
        return reverse('department_detail', kwargs={'slug': self.slug})

    @property
    def get_lalala(self):
        return f'department + {self.slug}'

class Category(models.Model):
    name = models.CharField(max_length=100)
    department  = models.ForeignKey('Department',  on_delete=models.CASCADE,related_name='categories', null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    id_pai = models.IntegerField(null=True, blank=True)
    descricao = models.CharField(max_length=255,null=True, blank=True)
    descricao_completa = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def parent(self):
        if self.id_pai:
            return Department.objects.get(id=self.id_pai)

        return None

    @property
    def children(self):
        return self.objects.filter(id_pai=self.id)

    @property
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})



class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    image_thumbnail = ImageSpecField(source='image',
                                     processors=[ResizeToFill(100, 100)],
                                     format='JPEG',
                                     options={'quality': 60})
    image_url = models.URLField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Verifica se uma imagem com o mesmo nome já existe
        existing_image = ProductImage.objects.filter(product=self.product, image=self.image.name).first()
        if existing_image and existing_image != self:
            # Substitui a imagem existente
            existing_image.image.delete(save=False)  # Deleta a imagem antiga
            existing_image.image = self.image  # Atualiza para a nova imagem
            existing_image.save()
        else:
            super().save(*args, **kwargs)



class ProductReview(models.Model):
    from usuario.models import UserProfile

    user_profile = models.ForeignKey(UserProfile, related_name='reviews', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Substitua 'Product' pelo seu modelo de produto
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user_profile.user.username} on {self.product.name}"



from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class StockHistory(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    date_changed = models.DateTimeField(auto_now_add=True)
    old_stock = models.IntegerField()
    new_stock = models.IntegerField()

    def __str__(self):
        return f"Stock history for {self.content_object} on {self.date_changed}"

def update_stock_history(instance, old_stock, new_stock):
    print('update_stock_history')
    content_type = ContentType.objects.get_for_model(instance)
    StockHistory.objects.create(
        content_type=content_type,
        object_id=instance.id,
        old_stock=old_stock,
        new_stock=new_stock
    )
