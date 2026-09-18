from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models.core import GoalComment
from core.models.notification import Notification


@receiver(post_save, sender=GoalComment)
def create_comment_notification(sender, instance, created, **kwargs):
    # نعمل فقط عند إنشاء تعليق جديد وليس عند التعديل
    if not created:
        return

    comment_author = instance.user      # الشخص الذي كتب التعليق الحالي
    goal = instance.goal                # الهدف المرتبط
    student = goal.user                 # الطالب صاحب الهدف

    # 1. إذا كان كاتب التعليق شخص آخر غير الطالب (مثل المشرف أو الآدمن)
    if comment_author != student:
        message = f"قام {comment_author.get_full_name() or comment_author.username} بإضافة تعليق على هدفك: '{goal.title}'"
        Notification.objects.create(
            user=student,
            goal=goal,
            message=message
        )

# 2. إذا كان كاتب التعليق هو الطالب نفسه (رد على التعليقات)
    else:
        # جميع المعلقين السابقين (باستثناء الطالب)
        recipients_ids = set(
            goal.comments.exclude(user=student)
                         .values_list('user_id', flat=True)
        )

        # إذا كان للطالب مشرف، نضيفه لقائمة المستلمين حتى لو لم يعلق من قبل
        if student.supervisor:
            recipients_ids.add(student.supervisor.id)

        # إرسال إشعار لكل مستلم
        for user_id in recipients_ids:
            message = f"قام الطالب {student.get_full_name() or student.username} بإضافة تعليق/رد على الهدف: '{goal.title}'"
            Notification.objects.create(
                user_id=user_id,
                goal=goal,
                message=message
            )