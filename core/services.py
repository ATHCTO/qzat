# core/services.py
from django.utils import timezone
from datetime import timedelta
from .models import Goal, Notification

def check_and_send_goal_notifications():
    now = timezone.now()
    
    # -------------------------------------------------------------
    # 1. إشعارات الـ 24 ساعة
    # -------------------------------------------------------------
    notice_24h_threshold = now + timedelta(hours=24)
    
    goals_24h = Goal.objects.filter(
        status=Goal.Status.IN_PROGRESS,
        notified_24h=False,
        due_datetime__gt=now,
        due_datetime__lte=notice_24h_threshold
    )
    
    for goal in goals_24h:
        Notification.objects.create(
            user=goal.user,
            goal=goal,
            message=f'⏳ تذكير: متبقي 24 ساعة فقط على موعد إنجاز هدفك: "{goal.title}". شارفت على الوصول!'
        )
        goal.notified_24h = True
        goal.save(update_fields=['notified_24h'])

    # -------------------------------------------------------------
    # 2. إشعارات الساعتين
    # -------------------------------------------------------------
    notice_2h_threshold = now + timedelta(hours=2)
    
    goals_2h = Goal.objects.filter(
        status=Goal.Status.IN_PROGRESS,
        notified_2h=False,
        due_datetime__gt=now,
        due_datetime__lte=notice_2h_threshold
    )
    
    for goal in goals_2h:
        Notification.objects.create(
            user=goal.user,
            goal=goal,
            message=f'⚡ تنبيه عاجل: متبقي ساعتان فقط على نهاية وقت هدفك: "{goal.title}". لم يتبقَّ الكثير!'
        )
        goal.notified_2h = True
        goal.save(update_fields=['notified_2h'])