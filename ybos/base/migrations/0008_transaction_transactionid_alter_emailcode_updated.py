# Generated by Django 5.1.6 on 2025-03-10 05:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_alter_emailcode_updated_alter_transaction_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='transactionId',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='emailcode',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 10, 6, 18, 17, 277321)),
        ),
    ]
