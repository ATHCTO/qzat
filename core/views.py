from django.utils import timezone

from django.contrib import messages
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required

from core.models import Category, Domain, Track, Goal


def index(request):
    # حساب أعداد الأهداف حسب الحالة
    completed_goals_count = Goal.objects.filter(status=Goal.Status.COMPLETED).count()
    in_progress_goals_count = Goal.objects.filter(status=Goal.Status.IN_PROGRESS).count()
    extended_goals_count = Goal.objects.filter(status=Goal.Status.EXTENDED).count()
    
    # حساب عدد المجالات الفعلية المسجلة (أو ترك 18 ثابتة إذا كانت ثوابت الجمعية)
    total_domains_count = Domain.objects.count()

    context = {
        'completed_goals_count': completed_goals_count,
        'in_progress_goals_count': in_progress_goals_count,
        'extended_goals_count': extended_goals_count,
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
    
    # التعامل مع إضافة هدف جديد عند إرسال الفورم
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        raw_datetime = request.POST.get('due_datetime')

        if title and raw_datetime:
            naive_dt = parse_datetime(raw_datetime)
            aware_dt = make_aware(naive_dt) if naive_dt else None
            Goal.objects.create(
                domain=domain,
                track=track,
                title=title,
                description=description,
                due_datetime=aware_dt
            )
            messages.success(request, 'تمت إضافة الهدف بنجاح!')
            return redirect('track_goals', domain_id=domain.id, track_id=track.id)

    # جلب الأهداف الخاصة بهذا المجال والمسار
    goals = Goal.objects.filter(domain=domain, track=track).order_by('due_datetime')
    
    context = {
        'domain': domain,
        'track': track,
        'goals': goals,
    }
    return render(request, 'core/track_goals.html', context)

def edit_goal_view(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id)
    
    # التحقق من شرط الساعة
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
    
    # التحقق من شرط الساعة
    if not goal.is_editable():
        messages.error(request, 'عفواً، انتهت المهلة المحددة (ساعة واحدة) لحذف هذا الهدف!')
    else:
        goal.delete()
        messages.success(request, 'تم حذف الهدف بنجاح!')

    return redirect('track_goals', domain_id=goal.domain.id, track_id=goal.track.id)


def dashboard_view(request):
    total_goals = Goal.objects.count()
    completed_goals = Goal.objects.filter(status=Goal.Status.COMPLETED).count()
    in_progress_goals = Goal.objects.filter(status=Goal.Status.IN_PROGRESS).count()
    delayed_goals = Goal.objects.filter(status=Goal.Status.DELAYED).count()
    
    completion_rate = round((completed_goals / total_goals * 100), 1) if total_goals > 0 else 0
    domains_progress = Domain.objects.annotate(total=Count('goals'), completed=Count('goals', filter=Q(goals__status=Goal.Status.COMPLETED)))
    
    for domain in domains_progress:
        domain.percentage = round((domain.completed / domain.total * 100), 1) if domain.total > 0 else 0
        
    recent_goals = Goal.objects.select_related('domain', 'track').order_by('-created_at')[:5]
    
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
        # تأكيد الإنجاز وتحديد وقت الإنجاز الفعلي
        goal.status = 'COMPLETED'
        goal.completed_at = timezone.now()
        goal.save()
        messages.success(request, f'أحسنت! تم إنجاز الهدف "{goal.title}" بنجاح 👏')

    return redirect('track_goals', domain_id=goal.domain.id, track_id=goal.track.id)


def about_view(request):
    return render(request, 'core/about.html')


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        messages.success(request, f'شكراً للتواصل معنا يا {name}! تم استلام رسالتك وسنرد عليك في أقرب وقت.')
        return redirect('contact')

    return render(request, 'core/contact.html')