from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from user.models import CustomUser


@login_required(login_url='login')
def supervisor_students_list_view(request):
    if request.user.role not in [CustomUser.Role.SUPERVISOR, CustomUser.Role.MANAGER, CustomUser.Role.SYSTEM_ADMIN]:
        raise PermissionDenied("عذراً، هذه الصفحة مخصصة للمشرفين فقط.")
    
    my_students = request.user.students.all()
    
    context = {
        'students': my_students,
    }
    return render(request, 'core/supervisor/students_list.html', context)


@login_required(login_url='login')
def supervisor_student_detail_view(request, student_id):
    if request.user.role in [CustomUser.Role.SYSTEM_ADMIN, CustomUser.Role.MANAGER]:
        student = get_object_or_404(CustomUser, id=student_id, role=CustomUser.Role.STUDENT)
    else:
        student = get_object_or_404(CustomUser, id=student_id, supervisor=request.user)
        
        student_goals = student.goals.all() if hasattr(student, 'goals') else []
        
        now = timezone.now()
        
        context = {
        'student': student,
        'goals': student_goals,
        'now': now,
    }
    return render(request, 'core/supervisor/student_detail.html', context)
