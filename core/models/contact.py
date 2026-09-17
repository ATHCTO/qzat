from django.db import models


class ContactMessage(models.Model):
    STATUS_CHOICES = (
        ('new', 'جديدة'),
        ('read', 'تمت قراءتها'),
        ('replied', 'تم الرد'),
    )

    name = models.CharField(max_length=150, verbose_name="اسم المرسل")
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    subject = models.CharField(max_length=255, verbose_name="عنوان الموضوع")
    message = models.TextField(verbose_name="نص الرسالة")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new', verbose_name="حالة الرسالة")

    class Meta:
        verbose_name = "رسالة تواصل"
        verbose_name_plural = "رسائل التواصل"
        ordering = ['-created_at']

    def __str__(self):
        return f"رسالة من {self.name} - {self.subject}"


