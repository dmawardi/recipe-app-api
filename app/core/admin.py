"""Django admin customization."""
from django.contrib import admin
# base user admin class
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# import models
from core import models
# import translation system utilities
from django.utils.translation import gettext_lazy as _


# Register your models here.

class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name']
    # This needs to be added to allow editing of the user
    # This is because we replaced the default behaviour
    fieldsets = (
        # None for title, 2 fields: email & password
        (None, {"fields": ('email', 'password')}),
        (
            # Use Django translations to translate
            # Permissions for title
            _('Permissions'), {
                'fields': ('is_active', 'is_staff', 'is_superuser',)}
        ),
        (
            _('Important Dates'), {
                'fields': ('last_login',)
            }
        )
    )
    readonly_fields = ['last_login']
    # fieldsets for add form
    # Required changing due to modifications from default
    add_fieldsets = (
        (None, {
            # Add optional css class to make fields slightly more spaced
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser'
            )
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)
