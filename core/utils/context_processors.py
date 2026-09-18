from core.models.notification import Notification

def notifications_processor(request):
    if request.user.is_authenticated:
        # جلب أول 10 إشعارات للمستخدم الحالي
        user_notifications = Notification.objects.filter(user=request.user)[:10]
        # حساب عدد الإشعارات غير المقروءة
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        return {
            'notifications': user_notifications,
            'unread_notifications_count': unread_count,
        }
    return {
        'notifications': [],
        'unread_notifications_count': 0,
    }