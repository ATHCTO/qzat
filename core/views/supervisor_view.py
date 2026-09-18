from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.contrib import messages
from django.utils.dateparse import parse_datetime

from user.models.custom_user import CustomUser
from core.models.core import Goal
from core.models.notification import Notification

from core.utils.tasks import send_whatsapp_message


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
        
    student_goals = student.goals.all() if hasattr(student, 'goals') else Goal.objects.filter(user=student)
    
    now = timezone.now()
    
    context = {
        'student': student,
        'goals': student_goals,
        'now': now,
    }
    return render(request, 'core/supervisor/student_detail.html', context)


@login_required(login_url='login')
def extend_goal_time_view(request, goal_id):
    if request.method == 'POST':
        goal = get_object_or_404(Goal, id=goal_id)
        
        # التأكد من صلاحية المشرف/المدير
        if request.user.role not in [CustomUser.Role.SYSTEM_ADMIN, CustomUser.Role.MANAGER] and goal.user.supervisor != request.user:
            messages.error(request, "ليس لديك صلاحية لتعديل هذا الهدف.")
            return redirect('supervisor_students_list')

        new_due_str = request.POST.get('new_due_datetime')
        
        if new_due_str:
            parsed_datetime = parse_datetime(new_due_str)

            if parsed_datetime is not None:
                if timezone.is_naive(parsed_datetime):
                    parsed_datetime = timezone.make_aware(parsed_datetime, timezone.get_current_timezone())

                goal.due_datetime = parsed_datetime
                goal.status = 'EXTENDED'  # تحديث الحالة إلى ممدد
                goal.save()

                msg_text = f"مرحباً {goal.user.first_name}، قام المشرف بتمديد وقت الهدف '{goal.title}' إلى {goal.due_datetime.strftime('%Y-%m-%d %H:%M')}."
                
                # إنشاء الإشعار بحقول الموديل الصحيحة
                Notification.objects.create(
                    user=goal.user,
                    goal=goal,
                    category=Notification.Category.GOAL_ASSIGNED,  # أو الفئة المناسبة لديك مثل SYSTEM
                    type='whatsapp',  # أو البريد الإلكتروني حسب تفضيل النظام
                    message=msg_text,
                    is_read=False
                )

                if goal.user.phone_number:
                    send_whatsapp_message(phone_number=goal.user.phone_number, message_text=msg_text)
                    
                messages.success(request, f"تم تمديد وقت الهدف '{goal.title}' بنجاح وإرسال إشعار للطالب.")
            else:
                messages.error(request, "صيغة التاريخ والوقت المدخلة غير صحيحة.")
        else:
            messages.error(request, "الرجاء تحديد تاريخ ووقت صحيح.")

        return redirect('supervisor_student_detail', student_id=goal.user.id)
    
    return redirect('supervisor_students_list')