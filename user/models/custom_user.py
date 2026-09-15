from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone

from .address import Address


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        SYSTEM_ADMIN = 'SYSTEM_ADMIN', 'مدير النظام'
        MANAGER = 'MANAGER', 'مدير'
        SUPERVISOR = 'SUPERVISOR', 'مشرف'
        FACILITATOR = 'FACILITATOR', 'ميسّر'
        STUDENT = 'STUDENT', 'طالب'

    class IdentityType(models.TextChoices):
        NATIONAL_ID = 'NATIONAL_ID', 'هوية وطنية'
        RESIDENCE_ID = 'RESIDENCE_ID', 'هوية مقيم'
        
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
        null=True,
        blank=True,
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

    identity_type = models.CharField(
        max_length=20,
        choices=IdentityType.choices,
        default=IdentityType.NATIONAL_ID,
        verbose_name='نوع الهوية'
    )

    identity_number_regex = RegexValidator(
        regex=r'^[0-9]{10}$',
        message="رقم الهوية يجب أن يتكون من 10 أرقام فقط."
    )

    identity_number = models.CharField(
        validators=[identity_number_regex],
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        verbose_name='رقم الهوية',
        error_messages={'unique': 'رقم الهوية مستخدم بالفعل.'}
    )

    nationality = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='الجنسية'
    )

    address = models.ForeignKey(
        Address, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='users', 
        verbose_name='العنوان'
    )
    
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاريخ الميلاد'
    )
    
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        full_name = self.get_full_name().strip()
        display_name = full_name if full_name else self.username
        return f"{display_name} - ({self.get_role_display()})"
    
    @property
    def age(self):
        """حساب العمر بالسنوات بناءً على تاريخ الميلاد"""
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None