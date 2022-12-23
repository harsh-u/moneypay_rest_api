# Register your models here.
from django.contrib import admin
from .models import User, Account, Balance, Transactions, Method


# class UserAdmin(admin.ModelAdmin):
#     list_display = ('phone_number',)
#     readonly_fields = ('updated_at',)


class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_status')


class BalanceAdmin(admin.ModelAdmin):
    list_display = ('account', 'balance', 'currency')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'amount', 'sender', 'receiver')


admin.site.register(User)  #
admin.site.register(Account, AccountAdmin)
admin.site.register(Balance, BalanceAdmin)
admin.site.register(Transactions, TransactionAdmin)
admin.site.register(Method)
