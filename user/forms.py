from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'phone_number', 
            'identity_type',
            'identity_number',
            'nationality',
            'region',
            'birth_date',
            'role', 
            'supervisor'
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المستخدم'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الأول'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم العائلة'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0591234567'}),
            'identity_type': forms.Select(attrs={'class': 'form-select'}),
            'identity_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهوية (10 أرقام)'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الجنسية (مثال: سعودي)'}),
            'region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'المنطقة (مثال: الرياض)'}),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'supervisor': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'كلمة المرور'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'تأكيد كلمة المرور'})