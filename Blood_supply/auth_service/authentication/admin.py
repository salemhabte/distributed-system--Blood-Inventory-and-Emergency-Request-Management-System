from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin for User model with role-based fields
    """
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'role', 'organization_name', 'is_verified', 'is_active'
    )
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'organization_name')

    fieldsets = UserAdmin.fieldsets + (
        ('Role & Organization', {
            'fields': ('role', 'organization_name', 'phone_number', 'address', 'is_verified')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role & Organization', {
            'fields': ('role', 'organization_name', 'phone_number', 'address', 'is_verified')
        }),
    )
