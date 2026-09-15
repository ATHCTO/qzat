from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from user.models.custom_user import CustomUser
from user.forms import AdminUserCreationForm


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