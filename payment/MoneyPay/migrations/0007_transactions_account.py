# Generated by Django 4.1.4 on 2022-12-22 08:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('MoneyPay', '0006_remove_balance_amt_credit_remove_balance_amt_debit_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactions',
            name='account',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='MoneyPay.account', unique=True),
            preserve_default=False,
        ),
    ]
