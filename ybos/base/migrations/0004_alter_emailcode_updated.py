# Generated by Django 5.1.6 on 2025-03-05 17:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_alter_emailcode_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailcode',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 5, 17, 36, 53, 796806, tzinfo=datetime.timezone.utc)),
            preserve_default=False,
        ),
    ]
