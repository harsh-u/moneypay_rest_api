# Generated by Django 4.1.4 on 2022-12-21 14:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MoneyPay', '0003_alter_method_payment_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balance',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MoneyPay.account', unique=True),
        ),
    ]