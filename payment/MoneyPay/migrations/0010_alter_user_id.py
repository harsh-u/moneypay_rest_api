# Generated by Django 3.2.9 on 2023-01-24 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MoneyPay', '0009_auto_20221231_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
