from django.db import models
from usuario.models import UserProfile
from products.models import Product

class AviseItem(models.Model):
    user_profile = models.ForeignKey(UserProfile, related_name='avise', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Substitua 'Product' pelo seu modelo de produto
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    email_sent = models.BooleanField(default=False)
    email_sent_on = models.DateTimeField(null=True, blank=True)



    @property
    def product_id(self):

        return self.product.id

    def __str__(self):
        return str(self.product.id)

