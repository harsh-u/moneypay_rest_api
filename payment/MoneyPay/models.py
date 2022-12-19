from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


# Create your models here.


class User(AbstractUser):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: "
                                                                   "'+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    # created_at = models.DateTimeField(auto_now_add=True)  already available in AbstractUser as date_joined


class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = [
        ('1', 'Active'),
        ('2', 'Closed'),
    ]
    current_status = models.CharField(max_length=16, choices=status, default='Active')

    def __str__(self):
         return self.user.first_name


class Balance(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amt_credit = models.IntegerField()
    amt_debit = models.IntegerField()
    currency = models.CharField(max_length=3, blank=True)

    def get_balance(self, amt_credit=None, amt_debit=None):
        return (amt_credit - amt_debit) / 100.0  # It should always comes like 200.50, 20.00, that

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
    amount = models.IntegerField()
    sender = models.ForeignKey(User, related_name="sender", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="receiver", on_delete=models.CASCADE)
    # method = models.ForeignKey(Method, on_delete=models.CASCADE)



