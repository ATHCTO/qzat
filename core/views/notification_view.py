from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from core.models.notification import Notification

@login_required(login_url='login')
def read_and_redirect_notification(request, notification_id):
    # جلب الإشعار الخاص بالمستخدم الحالي
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    
    # تحويل حالة الإشعار إلى مقروء إذا لم يكن مقروءاً بالفعل
    if not notification.is_read:
        notification.is_read = True
        notification.save()
    
    # التوجيه للهدف المرتبط بالإشعار
    if notification.goal:
        return redirect('goal_detail', goal_id=notification.goal.id)
    
    # مسار احتياطي في حال عدم وجود هدف مرتبط
    return redirect('home')

@login_required(login_url='login')
def mark_all_notifications_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def notification_list(view_request):
    # جلب إشعارات المستخدم الحالية مرتبة من الأحدث للأقدم
    notifications = Notification.objects.filter(user=view_request.user).order_by('-created_at')
    
    # حساب عدد الإشعارات غير المقروءة
    unread_count = notifications.filter(is_read=False).count()

    return render(view_request, 'core/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def mark_notification_as_read(view_request, pk):
    # تحديد إشعار معين كمقروء
    notification = get_object_or_404(Notification, pk=pk, user=view_request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    
    return redirect('notification_list')

@login_required
def mark_all_notifications_as_read(view_request):
    # تحديد كافة الإشعارات كمقروءة دفعة واحدة
    Notification.objects.filter(user=view_request.user, is_read=False).update(is_read=True)
    return redirect('notification_list')