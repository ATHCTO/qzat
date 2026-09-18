# from celery import shared_task

# from core.models.core import Goal
# from core.models.notification import Notification
# from .whatsapp import send_whatsapp_message


# @shared_task
# def send_due_notification(goal_id, notification_type):
#     try:
#         goal = Goal.objects.get(id=goal_id)
        
#         # إذا تم إكمال الهدف قبل حلول الموعد، لا نرسل الإشعار
#         if goal.status == 'COMPLETED':
#             return
        
#         user = goal.user
        
#         user_phone = getattr(user, 'phone_number', None)

#         if notification_type == '24h':
#             message = f"⏰ تذكير: باقي 24 ساعة على موعد تسليم هدفك: '{goal.title}'"
#             goal.notified_24h = True
#             goal.save(update_fields=['notified_24h'])
            
#         elif notification_type == '3h':
#             message = f"🚨 تنبيه عاجل: ينتهي موعد هدفك '{goal.title}' خلال 3 ساعات فقط!"
#             goal.notified_3h = True
#             goal.save(update_fields=['notified_3h'])
#         else:
#             return

#         # إنشاء الإشعار في قاعدة البيانات
#         Notification.objects.create(
#             user=user,
#             goal=goal,
#             message=message
#         )
        
#         if user_phone:
#             send_whatsapp_message(phone_number=user_phone, message_text=message)
#     except Goal.DoesNotExist:
#         pass
    
    
from celery import shared_task
from core.models.core import Goal
from core.models.notification import Notification
from .whatsapp import send_whatsapp_message

@shared_task
def send_due_notification(goal_id, notification_type):
    try:
        goal = Goal.objects.get(id=goal_id)
        
        # إذا تم إكمال الهدف لا نرسل الإشعار
        if goal.status == 'COMPLETED':
            return

        user = goal.user
        
        # جلب الاسم ورقم الهاتف ومجال الهدف
        user_name = user.get_full_name() or user.username or "المستخدم"
        user_phone = getattr(user, 'phone_number', None)
        
        # افترضنا هنا وجود علاقة أو مجال باسم domain أو field على الهدف
        domain_name = getattr(goal.domain, 'name', 'المحدد') if hasattr(goal, 'domain') and goal.domain else "المحدد"

        if notification_type == '24h':
            message = f"""حياك الله أ/ {user_name} 🌿

🚀 اقتربت من خط النهاية!

تبقّى يوم واحد على الموعد المحدد لهدفك في مجال ({domain_name})

هدفك 🎯
«{goal.title}»

واصل تقدمك، وأكمل ما بدأت به بعزيمة وثبات.
خطوة أخيرة تفصلك عن تحقيق هدفك بإذن الله ✨

منصة قيادة الذات"""

            goal.notified_24h = True
            goal.save(update_fields=['notified_24h'])

        elif notification_type == '3h':
            message = f"""حياك الله أ/ {user_name} 🌿

🚨 تنبيه عاجل!

تبقّت 3 ساعات فقط على الموعد المحدد لهدفك في مجال ({domain_name})

هدفك 🎯
«{goal.title}»

واصل تقدمك بخطوات سريعة وثابتة لإنهاء هدفك بنجاح ✨

منصة قيادة الذات"""

            goal.notified_3h = True
            goal.save(update_fields=['notified_3h'])

        else:
            return

        # 1. حفظ الإشعار الداخلي في قاعدة البيانات
        Notification.objects.create(
            user=user,
            goal=goal,
            message=message
        )

        # 2. إرسال الرسالة عبر الواتساب (Green API)
        if user_phone:
            send_whatsapp_message(phone_number=user_phone, message_text=message)

    except Goal.DoesNotExist:
        pass