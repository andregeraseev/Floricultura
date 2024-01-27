from PIL import UnidentifiedImageError
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from .models import Product, ProductImage, ProductVariation, MateriaPrima, ProductMaterial, ProductVariationRawMaterial, \
    StockHistory
from django.utils.html import format_html

class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 0  # Você pode ajustar o número de formulários extras
    fields = ['external_id','nome','idMapeamento', 'skuMapeamento', 'codigo', 'gtin', 'price', 'promotional_price', 'estoqueAtual', 'grade']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Número de formas extras para mostrar por padrão
    fields = ('image', 'image_url',)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['external_id','name', 'image_thumbnail_tag', 'price', 'promotion_active', 'is_available', 'is_featured','skuMapeamento', 'idMapeamento', 'alerta_estoque',]
    list_filter = ('is_available', 'promotion_active', 'is_featured',)
    list_editable = ('is_available', 'promotion_active', 'is_featured',)
    search_fields = ('name',)

    inlines = [ProductImageInline, ProductVariationInline]
    def image_thumbnail_tag(self, obj):
        try:
            first_image = obj.images.first()  # Obtém a primeira imagem do produto
            if first_image and first_image.image_thumbnail.url:
                return format_html(
                    '<img src="{}" style="width: 50px; height: auto;"/>'.format(first_image.image_thumbnail.url))
        except UnidentifiedImageError:
            # Se houver um erro ao identificar a imagem, retorna um texto alternativo
            return "Imagem não identificada"
        except Exception as e:
            # Trata outros tipos de erros, se necessário
            return f"Erro: {e}"
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
    list_display = ('external_id', 'name', 'stock', 'skuMapeamento', 'idMapeamento')
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


class StockTypeFilter(admin.SimpleListFilter):
    title = 'stock type'
    parameter_name = 'stock_type'

    def lookups(self, request, model_admin):
        # Retorna uma lista de tuplas. Cada tupla contém o ID do ContentType e o nome do modelo.
        content_types = ContentType.objects.filter(model__in=['product', 'productvariation', 'materiaprima'])
        return [(ctype.id, ctype.model) for ctype in content_types]

    def queryset(self, request, queryset):
        if self.value():
            # Filtra o queryset com base no ID do ContentType selecionado.
            return queryset.filter(content_type_id=self.value())
        return queryset
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'date_changed', 'old_stock', 'new_stock', 'stock_change')
    list_filter = (StockTypeFilter, 'date_changed')
    search_fields = ('content_type__model', 'object_id')
    readonly_fields = ('content_object', 'date_changed', 'old_stock', 'new_stock', 'stock_change')

    def stock_change(self, obj):
        return obj.new_stock - obj.old_stock
    stock_change.short_description = 'Change in Stock'

admin.site.register(StockHistory, StockHistoryAdmin)
