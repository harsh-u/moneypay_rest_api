from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

# Create your models here.
from django.db.models import Sum


class User(AbstractUser):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: "
                                                                   "'+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=False, unique=True)
    updated_at = models.DateTimeField(auto_now=True)

    # created_at = models.DateTimeField(auto_now_add=True)  already available in AbstractUser as date_joined


class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = [
        ('Active', 'Active'),
        ('Closed', 'Closed'),
    ]
    current_status = models.CharField(max_length=16, choices=status, default='Active')

    def __str__(self):
        return self.user.first_name


class Balance(models.Model):
    account = models.ForeignKey(Account, unique=True, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, blank=True)

    # def get_balance(self):
    #     return self.balance  # It should always comes like 200.50, 20.00, that
    #
    # @staticmethod
    # def get_current_balance(account):
    #     balance = Transactions.objects.filter(receiver=account).aggregate(total=Sum('amount'))['total']
    #     return balance


class Method(models.Model):
    id = models.AutoField(primary_key=True)
    type = [
        ('CC', 'CC'),
        ('CASH', 'Cash'),
        ('UPI', 'UPI'),
    ]
    payment_type = models.CharField(max_length=16, choices=type, default='Online')

    def __str__(self):
        return self.payment_type


class Transactions(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    sender = models.ForeignKey(Account, related_name="sender", on_delete=models.CASCADE)
    receiver = models.ForeignKey(Account, related_name="receiver", on_delete=models.CASCADE)
    # method = models.ForeignKey(Method, on_delete=models.CASCADE)
