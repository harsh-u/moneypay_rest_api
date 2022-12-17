# Register your models here.
from django.contrib import admin
from .models import User, Account, Balance, Transactions, Method


class UserAdmin(admin.ModelAdmin):
    list_display = ('phone_number',)
    readonly_fields = ('updated_at',)

admin.site.register(User, UserAdmin)
admin.site.register(Account)
admin.site.register(Balance)
admin.site.register(Transactions)
admin.site.register(Method)
