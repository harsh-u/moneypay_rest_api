# Register your models here.
from django.contrib import admin
from django.contrib.auth import get_user_model

from . import models
from .models import User, Account, Balance, Transactions, Method
from django.contrib.auth.admin import UserAdmin


class UserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'updated_at']


class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_status')


class BalanceAdmin(admin.ModelAdmin):
    list_display = ('account', 'balance', 'currency')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'amount', 'sender', 'receiver')


admin.site.register(models.User, UserAdmin)  #
admin.site.register(Account, AccountAdmin)
admin.site.register(Balance, BalanceAdmin)
admin.site.register(Transactions, TransactionAdmin)
admin.site.register(Method)
