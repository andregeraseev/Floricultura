# Generated by Django 4.2.7 on 2023-12-01 14:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0008_address_session_alter_address_user_profile'),
        ('sessions', '0001_initial'),
        ('pedidos', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='shipping_zipcode',
            new_name='cep',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='shipping_country',
            new_name='pais',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipping_address',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipping_city',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipping_state',
        ),
        migrations.AddField(
            model_name='order',
            name='bairro',
            field=models.CharField(default=1, max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='cidade',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='complemento',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='destinatario',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='estado',
            field=models.CharField(choices=[('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')], default=1, max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='numero',
            field=models.CharField(default=1, max_length=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='observacoes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='rua',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='session_order_addresses', to='sessions.session'),
        ),
        migrations.AlterField(
            model_name='order',
            name='user_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='usuario.userprofile'),
        ),
    ]
