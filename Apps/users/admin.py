from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from django.contrib import admin
from . import models

class UserProfileAdmin(UserAdmin):
    list_display = ('username','ch_name', 'phone', 'email',
                    'department', 'role','is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('ch_name','phone', 'department', 'email')}),
        (('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'role','groups', 'user_permissions'),
        }),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(models.UserProfile, UserProfileAdmin)
