# Generated by Django 3.2.9 on 2023-02-02 06:49

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('MoneyPay', '0011_remove_user_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactions',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]