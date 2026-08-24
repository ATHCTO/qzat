from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        SYSTEM_ADMIN = 'SYSTEM_ADMIN', 'مدير النظام'
        MANAGER = 'MANAGER', 'مدير'
        SUPERVISOR = 'SUPERVISOR', 'مشرف'
        STUDENT = 'STUDENT', 'طالب'

    email = models.EmailField(
        unique=True, 
        verbose_name='البريد الإلكتروني', 
        error_messages={'unique': 'هذا البريد الإلكتروني مستخدم بالفعل.'}
    )
    
    phone_regex = RegexValidator(
        regex=r'^(05|\+9665)[0-9]{8}$',
        message="رقم الجوال يجب أن يكون بصيغة صحيحة (مثال: 0591234567 أو +966591234567)."
    )
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=15, 
        unique=True, 
        verbose_name='رقم الجوال', 
        error_messages={'unique': 'رقم الجوال مستخدم بالفعل.'}, 
        help_text='مثال: 0591234567 أو +966591234567'
    )
    
    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.STUDENT, 
        verbose_name='نوع المستخدم'
    )
    
    supervisor = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='students', 
        limit_choices_to={'role': Role.SUPERVISOR}, 
        verbose_name='المشرف المباشر'
    )

    # حلف المجموعات والصلاحيات لتفادي التعارض مع Django Auth الافتراضي
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='المجموعات'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='صلاحيات المستخدم'
    )

    REQUIRED_FIELDS = ['email', 'phone_number', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.get_full_name() or self.username} - ({self.get_role_display()})"