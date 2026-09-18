from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from core.models.core import Goal, Domain, Track, GoalComment
from user.models.custom_user import CustomUser


@login_required(login_url='login')
def track_goals_view(request, domain_id, track_id):
    domain = get_object_or_404(Domain, id=domain_id)
    track = get_object_or_404(Track, id=track_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        raw_start_datetime = request.POST.get('start_datetime')
        raw_due_datetime = request.POST.get('due_datetime')

        if title and raw_due_datetime:
            # تحويل تاريخ البدء إن وجد
            aware_start_dt = None
            if raw_start_datetime:
                naive_start_dt = parse_datetime(raw_start_datetime)
                aware_start_dt = make_aware(naive_start_dt) if naive_start_dt else None

            # تحويل تاريخ النهاية/الاستحقاق
            naive_due_dt = parse_datetime(raw_due_datetime)
            aware_due_dt = make_aware(naive_due_dt) if naive_due_dt else None

            # التحقق المنطقي من التواريخ في حالة الإدخال اليدوي عبر POST
            if aware_start_dt and aware_due_dt and aware_due_dt <= aware_start_dt:
                messages.error(request, 'عفواً، يجب أن يكون تاريخ الاستحقاق بعد تاريخ البدء!')
                return redirect('track_goals', domain_id=domain.id, track_id=track.id)

            Goal.objects.create(
                user=request.user,
                domain=domain,
                track=track,
                title=title,
                description=description,
                start_datetime=aware_start_dt,
                due_datetime=aware_due_dt
            )
            messages.success(request, 'تمت إضافة الهدف بنجاح!')
            return redirect('track_goals', domain_id=domain.id, track_id=track.id)

    goals = Goal.objects.filter(user=request.user, domain=domain, track=track).order_by('due_datetime')

    for goal in goals:
        goal.update_status()
    
    context = {
        'domain': domain,
        'track': track,
        'goals': goals,
    }
    return render(request, 'core/track_goals.html', context)


@login_required(login_url='login')
def edit_goal_view(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    
    if not goal.is_editable():
        messages.error(request, 'عفواً، انتهت المهلة المحددة (ساعة واحدة) لتعديل هذا الهدف!')
        return redirect('track_goals', domain_id=goal.domain.id, track_id=goal.track.id)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        raw_start_datetime = request.POST.get('start_datetime')
        raw_due_datetime = request.POST.get('due_datetime')

        if title and raw_due_datetime:
            aware_start_dt = None
            if raw_start_datetime:
                naive_start_dt = parse_datetime(raw_start_datetime)
                aware_start_dt = make_aware(naive_start_dt) if naive_start_dt else None

            naive_due_dt = parse_datetime(raw_due_datetime)
            aware_due_dt = make_aware(naive_due_dt) if naive_due_dt else None

            if aware_start_dt and aware_due_dt and aware_due_dt <= aware_start_dt:
                messages.error(request, 'عفواً، يجب أن يكون تاريخ الاستحقاق بعد تاريخ البدء!')
                return redirect('track_goals', domain_id=goal.domain.id, track_id=goal.track.id)

            goal.title = title
            goal.description = description
            goal.start_datetime = aware_start_dt
            goal.due_datetime = aware_due_dt

            # إعادة ضبط حالة الإشعارات ليعاد جدولة التنبيهات مع الموعد الجديد
            goal.notified_24h = False
            goal.notified_2h = False

            goal.save()
            messages.success(request, 'تم تعديل الهدف بنجاح!')
        
    return redirect('track_goals', domain_id=goal.domain.id, track_id=goal.track.id)


def delete_goal_view(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id)
    
    if not goal.is_editable():
        messages.error(request, 'عفواً، انتهت المهلة المحددة (ساعة واحدة) لحذف هذا الهدف!')
    else:
        goal.delete()
        messages.success(request, 'تم حذف الهدف بنجاح!')

    return redirect('track_goals', domain_id=goal.domain.id, track_id=goal.track.id)


@login_required(login_url='login')
def goal_detail_view(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id)

    is_owner = (goal.user == request.user)
    is_supervisor = (goal.user.supervisor == request.user)
    is_admin_or_manager = request.user.role in [CustomUser.Role.SYSTEM_ADMIN, CustomUser.Role.MANAGER]

    if not (is_owner or is_supervisor or is_admin_or_manager):
        raise PermissionDenied("عذراً، لا تملك صلاحية عرض هذا الهدف.")

    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            GoalComment.objects.create(
                goal=goal,
                user=request.user,
                comment=comment_text
            )
            messages.success(request, 'تمت إضافة التعليق بنجاح!')
            return redirect('goal_detail', goal_id=goal.id)
        else:
            messages.error(request, 'لا يمكن إضافة تعليق فارغ.')

    comments = goal.comments.all()
    context = {
        'goal': goal,
        'comments': comments,
    }
    return render(request, 'core/goal_detail.html', context)


def toggle_complete_goal_view(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id)

    if goal.status == 'COMPLETED':
        goal.status = Goal.Status.IN_PROGRESS
        goal.completed_at = None
        goal.save()
        messages.info(request, f'تمت إعادة الهدف "{goal.title}" إلى قائمة الأهداف قيد التنفيذ.')
    else:
        goal.status = 'COMPLETED'
        goal.completed_at = timezone.now()
        goal.save()
        messages.success(request, f'أحسنت! تم إنجاز الهدف "{goal.title}" بنجاح 👏')

    return redirect('track_goals', domain_id=goal.domain.id, track_id=goal.track.id)