from django.db import models
from usuario.models import UserProfile
from products.models import Product

class WishlistItem(models.Model):
    user_profile = models.ForeignKey(UserProfile, related_name='wishlist', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Substitua 'Product' pelo seu modelo de produto
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} - {self.user_profile.user.username}"


    @property
    def success_message(self):
        return f"Produto {self.product.name} adicionado aos favoritos com sucesso!"

    @property
    def delete_message(self):
        return f"Produto {self.product.name} foi tirado da sua lista de favoritos!"

    class Meta:
        verbose_name = ('wishlist item')
        verbose_name_plural = ('wishlist items')
        unique_together = ('user_profile', 'product')  # Para evitar itens duplicados na lista de desejos

