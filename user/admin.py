from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models.address import Address
from .models.custom_user import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 
        'get_full_name', 
        'email', 
        'identity_type', 
        'identity_number', 
        'phone_number', 
        'role', 
        'supervisor', 
        'display_age'
    )
    
    search_fields = (
        'username', 
        'email', 
        'phone_number', 
        'identity_number', 
        'first_name', 
        'last_name'
    )
    
    list_filter = (
        'role', 
        'identity_type', 
        'nationality', 
        'is_staff', 
        'is_active'
    )
    
    readonly_fields = ('display_age', 'last_login', 'date_joined')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('المعلومات الشخصية', {
            'fields': (
                ('first_name', 'last_name'),
                'email', 
                'phone_number',
                'birth_date',
                'display_age'
            )
        }),
        ('بيانات الهوية والإقامة', {
            'fields': (
                'identity_type', 
                'identity_number', 
                'nationality', 
            )
        }),
        ('الدور والإشراف', {'fields': ('role', 'supervisor')}),
        ('الصلاحيات', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('تواريخ هامة', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('المعلومات الشخصية والإضافية', {
            'fields': (
                'first_name', 
                'last_name', 
                'email', 
                'phone_number', 
                'identity_type', 
                'identity_number', 
                'nationality', 
                'birth_date', 
                'role', 
                'supervisor'
            ),
        }),
    )

    @admin.display(description='العمر (سنة)')
    def display_age(self, obj):
        return obj.age if obj.age is not None else "-"
    

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'region', 
        'city', 
        'street', 
        'building_number', 
        'additional_number', 
        'postal_code', 
        'national_address_code', 
        'geo_coordinates'
    )
    
    search_fields = (
        'region__name', 
        'city__name', 
        'street', 
        'building_number', 
        'additional_number', 
        'postal_code', 
        'national_address_code', 
        'geo_coordinates'
    )
    
    list_filter = (
        'region', 
        'city', 
        'street', 
        'building_number', 
        'additional_number', 
        'postal_code', 
        'national_address_code', 
        'geo_coordinates'
    )
    
    readonly_fields = ('geo_coordinates',)