# Generated by Django 4.2.7 on 2023-11-11 20:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_department_remove_category_image_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='category',
            new_name='department',
        ),
    ]
