from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib import messages

from core.models.core import Goal
from user.models.custom_user import CustomUser


@login_required(login_url='login')
def profile_view(request, user_id=None):
    if user_id:
        profile_user = get_object_or_404(CustomUser, id=user_id)
    else:
        profile_user = request.user

    if request.method == 'POST':
        if request.user != profile_user:
            messages.error(request, 'عفواً، لا يمكنك تعديل بيانات حساب آخر!')
            return redirect('profile')

        # استقبال البيانات من النموذج
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip() or None
        identity_type = request.POST.get('identity_type')
        identity_number = request.POST.get('identity_number', '').strip() or None
        nationality = request.POST.get('nationality', '').strip() or None
        birth_date = request.POST.get('birth_date') or None

        # التحقق من عدم تكرار البريد ورقم الهوية
        if email and email != profile_user.email:
            if CustomUser.objects.filter(email=email).exclude(id=profile_user.id).exists():
                messages.error(request, 'البريد الإلكتروني مُدخل بالفعل في حساب آخر!')
                return redirect('profile')

        if identity_number and identity_number != profile_user.identity_number:
            if CustomUser.objects.filter(identity_number=identity_number).exclude(id=profile_user.id).exists():
                messages.error(request, 'رقم الهوية مستخدم بالفعل في حساب آخر!')
                return redirect('profile')

        # تحديث البيانات
        profile_user.first_name = first_name
        profile_user.last_name = last_name
        profile_user.email = email
        profile_user.phone_number = phone_number
        profile_user.identity_type = identity_type
        profile_user.identity_number = identity_number
        profile_user.nationality = nationality
        profile_user.birth_date = birth_date
        profile_user.save()

        messages.success(request, 'تم تحديث بيانات الملف الشخصي بنجاح!')
        return redirect('profile')

    # حساب إحصائيات أهداف المستخدم
    goal_stats = Goal.objects.filter(user=profile_user).aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status=Goal.Status.COMPLETED))
    )

    context = {
        'profile_user': profile_user,
        'total_goals': goal_stats['total'] or 0,
        'completed_goals': goal_stats['completed'] or 0,
    }
    return render(request, 'user/profile.html', context)
