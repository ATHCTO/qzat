from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from core.models import Goal


def login_view(request):
    # إذا كان المستخدم مسجلاً دخوله بالفعل، نوجّهه للصفحة الرئيسية
    if request.user.is_authenticated:
        return redirect('index') # استبدل 'index' باسم الصفحة الرئيسية لديك

    if request.method == 'POST':
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')

        # التحقق من بيانات المستخدم
        user = authenticate(request, username=username_input, password=password_input)

        if user is not None:
            login(request, user)
            
            # إعادة التوجيه للصفحة المطلوبة إن وجدت أو الصفحة الرئيسية
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('index')  # استبدل باسم الصفحة الرئيسية لديك
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة. حاول مرة أخرى.')

    return render(request, 'user/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح. ننتظر عودتك قريبًا!')
    return redirect('login')


@login_required(login_url='login')
def profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        # تحديث بيانات المستخدم
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        messages.success(request, 'تم تحديث بيانات الملف الشخصي بنجاح!')
        return redirect('profile')

    # حساب إجمالي الأهداف والأهداف المكتملة بدون أخطاء الاستعلام
    total_goals = Goal.objects.count()
    completed_goals = Goal.objects.filter(status=Goal.Status.COMPLETED).count()

    context = {
        'user': user,
        'total_goals': total_goals,
        'completed_goals': completed_goals,
    }
    return render(request, 'user/profile.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import AdminUserCreationForm
from .models import CustomUser

@login_required
def create_user_by_admin(request):
    # 🔒 التحقق من الصلاحية: هل المستخدم مدير نظام أو مدير؟
    allowed_roles = [CustomUser.Role.SYSTEM_ADMIN, CustomUser.Role.MANAGER]
    
    if request.user.role not in allowed_roles and not request.user.is_superuser:
        messages.error(request, "عذراً، لا تملك الصلاحيات الكافية للوصول إلى هذه الصفحة.")
        return redirect('index')  # ↩️ إعادة التوجيه للصفحة الرئيسية فوراً (تأكد من اسم الـ URL لديك)

    # إذا كان مصرحاً له، يتم إكمال العملية بشكل طبيعي
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