# Generated by Django 5.1.6 on 2025-03-10 05:37

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_transaction_transactionid_alter_emailcode_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailcode',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 10, 6, 37, 27, 351851)),
        ),
        migrations.CreateModel(
            name='TransactionMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='transaction')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.transaction')),
            ],
        ),
    ]
