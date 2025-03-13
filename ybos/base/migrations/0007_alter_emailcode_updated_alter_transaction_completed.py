# Generated by Django 5.1.6 on 2025-03-10 05:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_alter_emailcode_updated_errorlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailcode',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 10, 6, 12, 28, 685674)),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='completed',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
