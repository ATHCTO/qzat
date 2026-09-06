from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q

from .forms import AdminUserCreationForm

from core.models import Goal
from .models import CustomUser


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')
        user = authenticate(request, username=username_input, password=password_input)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('index')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة. حاول مرة أخرى.')
    return render(request, 'user/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح. ننتظر عودتك قريبًا!')
    return redirect('login')


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
        region = request.POST.get('region', '').strip() or None
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
        profile_user.region = region
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

@login_required
def create_user_by_admin(request):
    allowed_roles = [CustomUser.Role.SYSTEM_ADMIN, CustomUser.Role.MANAGER]
    
    if request.user.role not in allowed_roles and not request.user.is_superuser:
        messages.error(request, "عذراً، لا تملك الصلاحيات الكافية للوصول إلى هذه الصفحة.")
        return redirect('index')
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"تم إنشاء حساب ({user.username}) بنجاح!")
            return redirect('create_user')
        else:
            messages.error(request, "يرجى تصحيح الأخطاء أدناه.")
    else:
        form = AdminUserCreationForm()

    return render(request, 'user/admin_panel/create_user.html', {'form': form})