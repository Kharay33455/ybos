# Generated by Django 5.1.6 on 2025-03-10 08:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_transaction_wassuccessful_alter_emailcode_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailcode',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 10, 9, 51, 45, 781179)),
        ),
    ]
