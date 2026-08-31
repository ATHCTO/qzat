import requests
from django.utils import timezone

from django.contrib import messages
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required

from .models import Category, Domain, Track, Goal,Camp, ContactMessage, GoalComment


@login_required(login_url='login')
def index(request):
    user = request.user

    # 1. تحديد نطاق الأهداف حسب دور المستخدم
    if user.role in [CustomUser.Role.SYSTEM_ADMIN, CustomUser.Role.MANAGER]:
        # مدير النظام والمدير: إحصائيات النظام بالكامل
        base_goals = Goal.objects.all()
        # إجمالي المجالات المتاحة في النظام
        total_domains_count = Domain.objects.count()

    elif user.role == CustomUser.Role.SUPERVISOR:
        # المشرف: إحصائيات الطلاب التابعين له فقط
        base_goals = Goal.objects.filter(user__supervisor=user)
        # عدد المجالات التي يستهدفها طلاب هذا المشرف
        total_domains_count = Domain.objects.filter(goals__user__supervisor=user).distinct().count()

    else:
        # الطالب: إحصائيات بياناته الشخصية فقط
        base_goals = Goal.objects.filter(user=user)
        # عدد المجالات التي لدى الطالب أهداف فيها
        total_domains_count = Domain.objects.filter(goals__user=user).distinct().count()

    # 2. حساب إحصائيات الأهداف في استعلام سريع واحد
    goal_stats = base_goals.aggregate(
        completed=Count('id', filter=Q(status=Goal.Status.COMPLETED)),
        in_progress=Count('id', filter=Q(status=Goal.Status.IN_PROGRESS)),
        extended=Count('id', filter=Q(status=Goal.Status.EXTENDED)),
    )

    context = {
        'completed_goals_count': goal_stats['completed'] or 0,
        'in_progress_goals_count': goal_stats['in_progress'] or 0,
        'extended_goals_count': goal_stats['extended'] or 0,
        'total_domains_count': total_domains_count,
    }
    return render(request, 'core/index.html', context)


def category_list(request):
    categories = Category.objects.prefetch_related('domains').all() 
    return render(request, 'core/category_list.html', {'categories': categories})


def domain_tracks_view(request, domain_id):
    domain = get_object_or_404(Domain.objects.prefetch_related('tracks'), id=domain_id)
    return render(request, 'core/domain_tracks.html', {'domain': domain})


@login_required(login_url='login')
def track_goals_view(request, domain_id, track_id):
    domain = get_object_or_404(Domain, id=domain_id)
    track = get_object_or_404(Track, id=track_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        raw_datetime = request.POST.get('due_datetime')

        if title and raw_datetime:
            naive_dt = parse_datetime(raw_datetime)
            aware_dt = make_aware(naive_dt) if naive_dt else None

            Goal.objects.create(
                user=request.user,
                domain=domain,
                track=track,
                title=title,
                description=description,
                due_datetime=aware_dt
            )
            messages.success(request, 'تمت إضافة الهدف بنجاح!')
            return redirect('track_goals', domain_id=domain.id, track_id=track.id)

    goals = Goal.objects.filter(user=request.user, domain=domain, track=track).order_by('due_datetime')
    
    context = {
        'domain': domain,
        'track': track,
        'goals': goals,
    }
    return render(request, 'core/track_goals.html', context)


@login_required(login_url='login')
def camp_list_view(request):
    camps = Camp.objects.filter(is_active=True).order_by('start_date')
    return render(request, 'core/camp_list.html', {'camps': camps})


@login_required(login_url='login')
def camp_detail_view(request, camp_id):
    camp = get_object_or_404(Camp, id=camp_id)
    
    if request.method == 'POST':
        # حماية: فقط الأدمن أو المدير يمكنه التعديل
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

    # إصلاح: عرض صفحة تفاصيل المعسكر وطبلته عند الـ GET
    students = camp.students.all()
    context = {
        'camp': camp,
        'students': students,
    }
    return render(request, 'core/camp_detail.html', context)


@login_required(login_url='login')
def edit_goal_view(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id, user=request.user)
    
    if not goal.is_editable():
        messages.error(request, 'عفواً، انتهت المهلة المحددة (ساعة واحدة) لتعديل هذا الهدف!')
        return redirect('track_goals', domain_id=goal.domain.id, track_id=goal.track.id)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        raw_datetime = request.POST.get('due_datetime')

        if title and raw_datetime:
            naive_dt = parse_datetime(raw_datetime)
            aware_dt = make_aware(naive_dt) if naive_dt else None
            goal.title = title
            goal.description = description
            goal.due_datetime = aware_dt
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
def dashboard_view(request):
    user = request.user

    # تحديد مجموعة الأهداف المسموح بعرضها حسب دور المستخدم
    if user.role in [CustomUser.Role.SYSTEM_ADMIN, CustomUser.Role.MANAGER]:
        base_goals = Goal.objects.all()
    elif user.role == CustomUser.Role.SUPERVISOR:
        # أهداف الطلاب التابعين لهذا المشرف
        base_goals = Goal.objects.filter(user__supervisor=user)
    else:
        # أهداف الطالب نفسه فقط
        base_goals = Goal.objects.filter(user=user)

    # 1. حساب الإحصائيات
    goal_stats = base_goals.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status=Goal.Status.COMPLETED)),
        in_progress=Count('id', filter=Q(status=Goal.Status.IN_PROGRESS)),
        delayed=Count('id', filter=Q(status=Goal.Status.DELAYED))
    )

    total_goals = goal_stats['total'] or 0
    completed_goals = goal_stats['completed'] or 0
    in_progress_goals = goal_stats['in_progress'] or 0
    delayed_goals = goal_stats['delayed'] or 0

    # 2. نسبة الإنجاز
    completion_rate = round((completed_goals / total_goals * 100), 1) if total_goals > 0 else 0

    # 3. التقدم في المجالات للمجموعة المستهدفة
    if user.role in [CustomUser.Role.SYSTEM_ADMIN, CustomUser.Role.MANAGER]:
        domains_progress = Domain.objects.annotate(
            total=Count('goals'),
            completed=Count('goals', filter=Q(goals__status=Goal.Status.COMPLETED))
        )
    elif user.role == CustomUser.Role.SUPERVISOR:
        domains_progress = Domain.objects.annotate(
            total=Count('goals', filter=Q(goals__user__supervisor=user)),
            completed=Count('goals', filter=Q(goals__user__supervisor=user, goals__status=Goal.Status.COMPLETED))
        )
    else:
        domains_progress = Domain.objects.annotate(
            total=Count('goals', filter=Q(goals__user=user)),
            completed=Count('goals', filter=Q(goals__user=user, goals__status=Goal.Status.COMPLETED))
        )

    for domain in domains_progress:
        domain.percentage = round((domain.completed / domain.total * 100), 1) if domain.total > 0 else 0

    # 4. آخر 5 أهداف
    recent_goals = base_goals.select_related('domain', 'track', 'user').order_by('-created_at')[:5]

    context = {
        'total_goals': total_goals,
        'completed_goals': completed_goals,
        'in_progress_goals': in_progress_goals,
        'delayed_goals': delayed_goals,
        'completion_rate': completion_rate,
        'domains_progress': domains_progress,
        'recent_goals': recent_goals,
    }
    return render(request, 'core/dashboard.html', context)


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


def about_view(request):
    return render(request, 'core/about.html')

import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail

def contact_view(request):
    if request.method == 'POST':
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': getattr(settings, 'RECAPTCHA_SECRET_KEY', 'YOUR_RECAPTCHA_SECRET_KEY'),
            'response': recaptcha_response
        }
        
        try:
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data, timeout=5)
            result = r.json()
        except requests.exceptions.RequestException:
            messages.error(request, 'تعذر التحقق من الكابتشا، يرجى المحاولة لاحقاً.')
            return redirect('contact')

        if not result.get('success'):
            messages.error(request, 'يرجى تأكيد أنك لست برنامج روبوت (reCAPTCHA).')
            return redirect('contact')

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not all([name, email, subject, message]):
            messages.error(request, 'جميع الحقول مطلوبة، يرجى إعادة المحاولة.')
            return redirect('contact')

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        email_body = f"رسالة جديدة من: {name}\nالبريد: {email}\nالموضوع: {subject}\n\nالنص:\n{message}"
        try:
            send_mail(
                subject=f"تواصل جديد: {subject}",
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, 'تم إرسال رسالتك بنجاح! سنقوم بالتواصل معك في أقرب وقت.')
        return redirect('contact')

    return render(request, 'core/contact.html')


def faq_view(request):
    return render(request, 'core/faq.html')


def privacy_view(request):
    return render(request, 'core/privacy.html')


def support_view(request):
    return render(request, 'core/support.html')

from django.core.exceptions import PermissionDenied

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


@login_required(login_url='login')
def goal_detail_view(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id)

    # التحقق من الصلاحيات: مسموح لصاحب الهدف، المشرف عليه، أو المدراء/الأدمن
    is_owner = (goal.user == request.user)
    is_supervisor = (goal.user.supervisor == request.user)
    is_admin_or_manager = request.user.role in [CustomUser.Role.SYSTEM_ADMIN, CustomUser.Role.MANAGER]

    if not (is_owner or is_supervisor or is_admin_or_manager):
        raise PermissionDenied("عذراً، لا تملك صلاحية عرض هذا الهدف.")

    # إضافة تعليق جديد
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


@login_required(login_url='login')
def edit_comment_view(request, comment_id):
    comment = get_object_or_404(GoalComment, id=comment_id)
    
    # التحقق من الملكية: صاحب التعليق فقط هو من يحق له تعديله
    if comment.user != request.user:
        messages.error(request, 'عفواً، يمكنك تعديل تعليقاتك الخاصة فقط!')
        return redirect('goal_detail', goal_id=comment.goal.id)

    # التحقق من مهلة الساعة
    if not comment.is_editable():
        messages.error(request, 'عفواً، انتهت المهلة المحددة (ساعة واحدة) لتعديل هذا التعليق!')
        return redirect('goal_detail', goal_id=comment.goal.id)

    if request.method == 'POST':
        new_text = request.POST.get('comment', '').strip()
        if new_text:
            comment.comment = new_text
            comment.save()
            messages.success(request, 'تم تعديل التعليق بنجاح!')
        else:
            messages.error(request, 'التعليق لا يمكن أن يكون فارغاً.')

    return redirect('goal_detail', goal_id=comment.goal.id)


@login_required(login_url='login')
def delete_comment_view(request, comment_id):
    comment = get_object_or_404(GoalComment, id=comment_id)
    goal_id = comment.goal.id

    # التحقق من الملكية
    if comment.user != request.user:
        messages.error(request, 'عفواً، يمكنك حذف تعليقاتك الخاصة فقط!')
        return redirect('goal_detail', goal_id=goal_id)

    # التحقق من مهلة الساعة
    if not comment.is_editable():
        messages.error(request, 'عفواً، انتهت المهلة المحددة (ساعة واحدة) لحذف هذا التعليق!')
        return redirect('goal_detail', goal_id=goal_id)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'تم حذف التعليق بنجاح!')

    return redirect('goal_detail', goal_id=goal_id)