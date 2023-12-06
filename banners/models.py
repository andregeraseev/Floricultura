from django.db import models
from django.utils import timezone
from django.conf import settings

class HeroBanner(models.Model):
    title = models.CharField(max_length=200, blank=True)
    title_active = models.BooleanField(default=False)
    image = models.ImageField(upload_to='hero_banners/')
    link = models.URLField(blank=True)
    description = models.TextField(blank=True)
    description_active = models.BooleanField(default=False)
    call = models.CharField(max_length=15, blank=True)
    call_active = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.title if self.title else "Hero Banner"

    @property
    def is_displayed(self):
        now = timezone.now()
        return self.is_active and (self.start_date <= now <= (self.end_date or now))


class SecondaryBanner(models.Model):
    title = models.CharField(max_length=200, blank=True)
    title_active = models.BooleanField(default=False)
    image = models.ImageField(upload_to='secondary_banners/')
    link = models.URLField(blank=True)
    description = models.TextField(blank=True)
    description_active = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title if self.title else "Secondary Banner"

    @property
    def is_displayed(self):
        now = timezone.now()
        return self.is_active and (self.start_date <= now <= (self.end_date or now))


from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

class BannerClick(models.Model):
    # Este campo irá apontar para o modelo HeroBanner ou SecondaryBanner
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    clicked_at = models.DateTimeField(default=timezone.now)
    clicked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Clique em {self.content_object.title} em {self.clicked_at}"

