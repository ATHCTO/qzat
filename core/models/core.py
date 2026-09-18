from django.db import models
from django.utils import timezone
from datetime import timedelta

from user.models.custom_user import CustomUser


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
    icon = models.CharField(max_length=100, blank=True, default='bi bi-layers', verbose_name='الرمز التعريفي للمجال')

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

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='goals', verbose_name='المستخدم')
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='goals', verbose_name='المجال')        
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='goals', verbose_name='المسار')
    title = models.CharField(max_length=150, verbose_name='عنوان الهدف')
    description = models.TextField(blank=True, verbose_name='الوصف')

    start_datetime = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ ووقت البدء")
    due_datetime = models.DateTimeField(verbose_name="تاريخ ووقت الاستحقاق")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ ووقت الإنجاز الفعلي")
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS, verbose_name='حالة التنفيذ')
    notes = models.TextField(blank=True, verbose_name='ملاحظات المشرف/الطالب')

    notified_24h = models.BooleanField(default=False)
    notified_3h = models.BooleanField(default=False)
    
    task_id_24h = models.CharField(max_length=255, null=True, blank=True)
    task_id_3h = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')

    class Meta:
        verbose_name = 'هدف'
        verbose_name_plural = 'الأهداف'
        ordering = ['due_datetime']

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
    
    @property
    def dynamic_status(self):
        """
        تحدد الحالة الحقيقية للحسابات والواجهة دون الانتظار لحفظها في قاعدة البيانات
        """
        # إذا تم إنجاز الهدف لا نتعدل عليه
        if self.status == self.Status.COMPLETED:
            return self.Status.COMPLETED

        # إذا تجاوز الوقت الحالي تاريخ الاستحقاق
        if timezone.now() > self.due_datetime:
            return self.Status.DELAYED

        return self.status

    def update_status(self):
        """
        تحديث حالة الهدف في قاعدة البيانات إذا أصبح متأخراً
        """
        if self.status != self.Status.COMPLETED and timezone.now() > self.due_datetime:
            if self.status != self.Status.DELAYED:
                self.status = self.Status.DELAYED
                self.save(update_fields=['status'])
        return self.status

    def is_delayed(self):
        """ترجع True إذا كان الهدف متأخراً وغير مكتمل"""
        return self.dynamic_status == self.Status.DELAYED
    
    
class Camp(models.Model):
    title = models.CharField(max_length=255, verbose_name='اسم المعسكر')
    description = models.TextField(blank=True, null=True, verbose_name='وصف المعسكر')
    start_date = models.DateField(verbose_name='تاريخ البداية')
    end_date = models.DateField(verbose_name='تاريخ النهاية')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    
    students = models.ManyToManyField(CustomUser, related_name='students_camps', blank=True, limit_choices_to={'role': CustomUser.Role.STUDENT}, verbose_name='الطلاب المشاركون')
    supervisors = models.ManyToManyField(CustomUser, related_name='supervisors_camps', blank=True, limit_choices_to={'role': CustomUser.Role.SUPERVISOR}, verbose_name='المشرفون')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')

    class Meta:
        verbose_name = 'معسكر'
        verbose_name_plural = 'المعسكرات'
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    @property
    def is_finished(self):
        """خاصية لمعرفة هل انتهى وقت المعسكر أم لا"""
        return timezone.now().date() > self.end_date
    
    
class GoalComment(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='comments', verbose_name='الهدف')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments', verbose_name='المستخدم')
    comment = models.TextField(verbose_name='التعليق')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التعديل')
    
    class Meta:
        verbose_name = 'تعليق عن الهدف'
        verbose_name_plural = 'تعليقات عن الأهداف'
        ordering = ['created_at']

    def __str__(self):
        return f"تعليق بواسطة {self.user.username} - {self.goal.title}"

    def is_editable(self):
        """فحص هل مضى أقل من ساعة واحدة على كتابة التعليق"""
        return timezone.now() <= self.created_at + timedelta(hours=1)

    @property
    def is_edited(self):
        """تحديد هل تم تعديل التعليق (بفارق أكثر من ثانيتين عن الإنشاء للتغلب على الفروق الدقيقة)"""
        return (self.updated_at - self.created_at).total_seconds() > 2
