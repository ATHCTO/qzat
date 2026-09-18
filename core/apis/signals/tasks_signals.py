from datetime import timedelta
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models.core import Goal
from core.utils.tasks import send_due_notification
from project.celery import app
@receiver(post_save, sender=Goal)
def schedule_goal_notifications(sender, instance, created, **kwargs):
    # إذا اكتمل الهدف، نلغي المهام إن وجدت
    if instance.status == 'COMPLETED':
        if instance.task_id_24h:
            app.control.revoke(instance.task_id_24h, terminate=True)
        if instance.task_id_3h:
            app.control.revoke(instance.task_id_3h, terminate=True)
        return

    now = timezone.now()

    # 1. جدولة إشعار الـ 24 ساعة
    if instance.due_datetime:
        eta_24h = instance.due_datetime - timedelta(seconds=10)
        if eta_24h > now:
            if instance.task_id_24h:
                app.control.revoke(instance.task_id_24h, terminate=True)
                
            task_24h = send_due_notification.apply_async(
                args=[instance.id, '24h'],
                eta=eta_24h
            )
            Goal.objects.filter(id=instance.id).update(task_id_24h=task_24h.id)

        # 2. جدولة إشعار الـ 3 ساعات
        eta_3h = instance.due_datetime - timedelta(hours=3)
        if eta_3h > now:
            if instance.task_id_3h:
                app.control.revoke(instance.task_id_3h, terminate=True)

            task_3h = send_due_notification.apply_async(
                args=[instance.id, '3h'],
                eta=eta_3h
            )
            Goal.objects.filter(id=instance.id).update(task_id_3h=task_3h.id)