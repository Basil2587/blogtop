# Generated by Django 2.2 on 2020-04-07 11:56

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_auto_20200406_0218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(default=uuid.uuid1, unique=True),
        ),
    ]
