from django.db import models
from django.utils import timezone
from datetime import timedelta


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='اسم المحور')
    description = models.TextField(blank=True, verbose_name='الوصف')
    
    class Meta:
        verbose_name = 'محور'
        verbose_name_plural = 'المحاور'

    def __str__(self):
        return self.name
    

class Track(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='اسم المسار')
    description = models.TextField(blank=True, verbose_name='وصف عام للمسار')

    class Meta:
        verbose_name = 'مسار'
        verbose_name_plural = 'المسارات'

    def __str__(self):
        return self.name
    

class Domain(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='domains', verbose_name='المحور')
    name = models.CharField(max_length=150, unique=True, verbose_name='اسم المجال')
    description = models.TextField(blank=True, verbose_name='الوصف')
    
    tracks = models.ManyToManyField(Track, related_name='domains', verbose_name='المسارات')
    class Meta:
        verbose_name = 'مجال'
        verbose_name_plural = 'المجالات'

    def __str__(self):
        return f"({self.category.name}) - {self.name}"
    

class Goal(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', 'قيد التنفيذ'
        COMPLETED = 'COMPLETED', 'مكتمل'
        DELAYED = 'DELAYED', 'متأخر'
        EXTENDED = 'EXTENDED', 'ممدد'

    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='goals', verbose_name='المجال')        
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='goals', verbose_name='المسار')
    title = models.CharField(max_length=150, verbose_name='عنوان الهدف')
    description = models.TextField(blank=True, verbose_name='الوصف')

    due_datetime = models.DateTimeField(verbose_name="الموعد الزمني للتنفيذ")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ ووقت الإنجاز الفعلي")
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS, verbose_name='حالة التنفيذ')
    notes = models.TextField(blank=True, verbose_name='ملاحظات المشرف/الطالب')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        verbose_name = 'هدف'
        verbose_name_plural = 'الأهداف'
        ordering = ['due_datetime']  # ترتيب الأهداف حسب الموعد الزمني للتنفيذ

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def is_editable(self):
        """ترجع True إذا لم تمضِ ساعة على إنشاء الهدف"""
        return (self.status != 'COMPLETED') and (timezone.now() <= self.created_at + timedelta(hours=1))

    def remaining_minutes_to_edit(self):
        """حساب الدقائق المتبقية لإمكانية التعديل"""
        if self.is_editable():
            diff = (self.created_at + timedelta(hours=1)) - timezone.now()
            return int(diff.total_seconds() // 60)
        return 0