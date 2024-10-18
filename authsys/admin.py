from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from . import models

# Register your models here.


# Register the UserModel on the admin interface
@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "usable_password", "password1", "password2", 'email', 'first_name', 'last_name'),
            },
        ),
    )
    list_display = ['id','first_name', 'last_name', 'email', 'is_staff', 'is_active']
    list_editable = ['is_active', 'is_staff']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['first_name']
