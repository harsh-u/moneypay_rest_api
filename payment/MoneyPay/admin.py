# Register your models here.
from django.contrib import admin
from .models import User, Account, Balance, Transactions, Method


# class UserAdmin(admin.ModelAdmin):
#     list_display = ('phone_number',)
#     readonly_fields = ('updated_at',)


class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_status')


class BalanceAdmin(admin.ModelAdmin):
    list_display = ('account', 'amt_credit', 'amt_debit', 'currency')


admin.site.register(User)  #
admin.site.register(Account, AccountAdmin)
admin.site.register(Balance, BalanceAdmin)
admin.site.register(Transactions)
admin.site.register(Method)
