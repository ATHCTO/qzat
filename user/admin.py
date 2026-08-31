from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # الحقول التي تظهر في جدول عرض المستخدمين
    list_display = ('username', 'email', 'phone_number', 'role', 'supervisor', 'is_staff')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    
    # حقول صفحة التعديل (Edit User)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('المعلومات الشخصية', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('الدور والإشراف', {'fields': ('role', 'supervisor')}),
        ('الصلاحيات', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تواريخ هامة', {'fields': ('last_login', 'date_joined')}),
    )

    # حقول صفحة إنشاء مستخدم جديد (Add User) - تضمن تشفير كلمة المرور تلقائياً
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('معلومات إضافية', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'role', 'supervisor'),
        }),
    )