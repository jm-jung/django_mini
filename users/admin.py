from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Users


@admin.register(Users)
class CustomerAdmin(UserAdmin):
    list_display = ('email', 'nickname', 'phone_number', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'nickname', 'phone_number')
    ordering = ('email',)
    readonly_fields = ('is_staff',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('nickname', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nickname', 'phone_number', 'password', 'password2')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('is_staff',)
        return self.readonly_fields

