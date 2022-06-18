"""Django admin customization."""
from django.contrib import admin
# base user admin class
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# import models
from core import models


# Register your models here.

class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name']


admin.site.register(models.User, UserAdmin)
