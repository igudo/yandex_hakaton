from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.conf import settings


class UserAccountAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Доп. поля', {'fields': (
        )}),
    )


admin.site.register(UserAccount, UserAccountAdmin)