# Generated by Django 4.2.7 on 2023-11-11 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_config', '0002_sitesettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='version_number',
            field=models.IntegerField(default=1),
        ),
    ]
