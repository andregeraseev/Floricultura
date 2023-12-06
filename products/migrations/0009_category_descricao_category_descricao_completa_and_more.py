# Generated by Django 4.2.7 on 2023-11-18 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_product_alturaembalagem_product_cest_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='descricao',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='descricao_completa',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='id_pai',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
