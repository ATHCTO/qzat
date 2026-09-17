from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from core.models.core import Camp
from user.models.custom_user import CustomUser


@login_required(login_url='login')
def camp_list_view(request):
    camps = Camp.objects.filter(is_active=True).order_by('start_date')
    return render(request, 'core/camp_list.html', {'camps': camps})


@login_required(login_url='login')
def camp_detail_view(request, camp_id):
    camp = get_object_or_404(Camp, id=camp_id)
    
    if request.method == 'POST':
        if request.user.role not in [CustomUser.Role.SYSTEM_ADMIN, CustomUser.Role.MANAGER]:
            messages.error(request, 'عفواً، لا تملك صلاحية تعديل بيانات المعسكر.')
            return redirect('camp_detail', camp_id=camp.id)

        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        if title and start_date and end_date:
            camp.title = title
            camp.description = description
            camp.start_date = start_date
            camp.end_date = end_date
            camp.save()
            messages.success(request, 'تم تحديث المعسكر بنجاح!')
            return redirect('camp_detail', camp_id=camp.id)

    students = camp.students.all()
    context = {
        'camp': camp,
        'students': students,
    }
    return render(request, 'core/camp_detail.html', context)


