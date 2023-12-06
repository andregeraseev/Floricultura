from django.contrib import admin
from .models import Product, ProductImage, ProductVariation,MateriaPrima, ProductMaterial, ProductVariationRawMaterial
from django.utils.html import format_html

class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 0  # Você pode ajustar o número de formulários extras
    fields = ['idMapeamento', 'skuMapeamento', 'codigo', 'gtin', 'price', 'promotional_price', 'estoqueAtual', 'grade']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Número de formas extras para mostrar por padrão
    fields = ('image', 'image_url',)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'image_thumbnail_tag', 'price', 'promotion_active', 'is_available']
    inlines = [ProductImageInline, ProductVariationInline]
    def image_thumbnail_tag(self, obj):
        first_image = obj.images.first()  # Obtém a primeira imagem do produto
        if first_image and first_image.image_thumbnail.url:
            return format_html('<img src="{}" style="width: 50px; height: auto;"/>'.format(first_image.image_thumbnail.url))
        return "-"
    image_thumbnail_tag.short_description = 'Thumbnail'

admin.site.register(Product, ProductAdmin)

from django.contrib import admin
from .models import Department, Category

class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1  # Número de formas extras para mostrar por padrão
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    inlines = [CategoryInline]
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')

    def created_at(self, obj):
        return obj.create_at

    def updated_at(self, obj):
        return obj.update_at

    created_at.short_description = 'Criado em'
    updated_at.short_description = 'Atualizado em'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'created_at', 'updated_at']
    list_filter = ('department',)
    search_fields = ('name', 'department__name')
    readonly_fields = ('created_at', 'updated_at')

    # raw_id_fields = ('department',)  # Ajuste para incluir apenas campos relacionais relevantes

    def created_at(self, obj):
        return obj.create_at

    def updated_at(self, obj):
        return obj.update_at

    created_at.short_description = 'Criado em'
    updated_at.short_description = 'Atualizado em'


class MateriaPrimaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'stock')
    search_fields = ('name',)

class ProductMaterialAdmin(admin.ModelAdmin):
    list_display = ('product', 'materia_prima', 'quantity_used')
    list_filter = ('product', 'materia_prima')
    search_fields = ('product__name', 'materia_prima__name')

class ProductVariationRawMaterialAdmin(admin.ModelAdmin):
    list_display = ('product_variation', 'materia_prima', 'quantity_used')
    list_filter = ('product_variation', 'materia_prima')
    search_fields = ('product_variation__product__name', 'materia_prima__name')
admin.site.register(MateriaPrima, MateriaPrimaAdmin)
admin.site.register(ProductMaterial, ProductMaterialAdmin)
admin.site.register(ProductVariationRawMaterial, ProductVariationRawMaterialAdmin)
