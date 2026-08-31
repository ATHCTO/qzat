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
            'role', 
            'supervisor'
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المستخدم'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الأول'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الاخير'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0591234567'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'supervisor': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تخصيص حقول كلمة المرور التابعة لـ UserCreationForm لتأخذ تنسيق Bootstrap
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'كلمة المرور'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'تأكيد كلمة المرور'})