# Generated by Django 2.1.1 on 2018-10-16 06:22

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0002_auto_20181013_0701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='afentorno',
            name='ent_config_file',
            field=models.FileField(blank=True, storage=django.core.files.storage.FileSystemStorage(location='/var/www/media/'), upload_to='', verbose_name='Fichero de entorno'),
        ),
    ]
