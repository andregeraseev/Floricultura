# Generated by Django 4.2.7 on 2023-11-28 13:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0004_address_destinatario'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='zipcode',
            new_name='cep',
        ),
        migrations.RenameField(
            model_name='address',
            old_name='city',
            new_name='cidade',
        ),
        migrations.RenameField(
            model_name='address',
            old_name='state',
            new_name='estado',
        ),
        migrations.RenameField(
            model_name='address',
            old_name='country',
            new_name='pais',
        ),
        migrations.RenameField(
            model_name='address',
            old_name='street',
            new_name='rua',
        ),
    ]
