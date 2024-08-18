from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['mobile', 'name', 'email', 'uid_no', 'is_staff', 'is_active', 'verified', 'account_balance']
    list_filter = ['is_staff', 'is_active', 'verified']
    fieldsets = (
        (None, {'fields': ('mobile', 'name', 'email', 'password', 'uid_no')}),
        ('Legs', {'fields': ('left_leg', 'middle_leg', 'right_leg')}),
        ('Account Info', {'fields': ('account_balance', 'verified', 'created_at', 'updated_at')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'name', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    readonly_fields = ('uid_no', 'created_at', 'updated_at')
    search_fields = ('mobile', 'email', 'uid_no')
    ordering = ('mobile',)

admin.site.register(CustomUser, CustomUserAdmin)
