from django.db import models
from django.urls import reverse

from user.models.custom_user import CustomUser
from .core import Goal


class Notification(models.Model):
    class Category(models.TextChoices):
        COMMENT = 'comment', 'تعليق جديد'
        GOAL_DUE = 'goal_due', 'اقتراب الموعد النهائي'
        GOAL_COMPLETED = 'goal_completed', 'إكمال هدف'
        GOAL_ASSIGNED = 'goal_assigned', 'إسناد هدف جديد'
        SYSTEM = 'system', 'نظام'

    category = models.CharField(
        max_length=20, 
        choices=Category.choices, 
        default=Category.COMMENT,
        verbose_name='تصنيف الإشعار'
    )
    type = models.CharField(max_length=10, choices=(('whatsapp', 'واتساب'), ('email', 'البريد الإلكتروني')), default='whatsapp', verbose_name='نوع الإشعار')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications', verbose_name='المستخدم')
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, null=True, blank=True, verbose_name='الهدف')
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def get_absolute_url(self):
        if self.goal:
            return reverse('goal_detail', kwargs={'goal_id': self.goal.id})
        return '#'