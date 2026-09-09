from django.shortcuts import render
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required

from core.models import Goal, Domain
from user.models.custom_user import CustomUser


def index_view(request):
    user = request.user

    if user.role in [CustomUser.Role.SYSTEM_ADMIN, CustomUser.Role.MANAGER]:
        base_goals = Goal.objects.all()
        total_domains_count = Domain.objects.count()

    elif user.role == CustomUser.Role.SUPERVISOR:
        base_goals = Goal.objects.filter(user__supervisor=user)
        total_domains_count = Domain.objects.filter(goals__user__supervisor=user).distinct().count()

    else:
        base_goals = Goal.objects.filter(user=user)
        total_domains_count = Domain.objects.filter(goals__user=user).distinct().count()

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

def faq_view(request):
    return render(request, 'core/faq.html')


def privacy_view(request):
    return render(request, 'core/privacy.html')


def support_view(request):
    return render(request, 'core/support.html')


@login_required(login_url='login')
def dashboard_view(request):
    user = request.user

    if user.role in [CustomUser.Role.SYSTEM_ADMIN, CustomUser.Role.MANAGER]:
        base_goals = Goal.objects.all()
    elif user.role == CustomUser.Role.SUPERVISOR:
        base_goals = Goal.objects.filter(user__supervisor=user)
    else:
        base_goals = Goal.objects.filter(user=user)

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

    completion_rate = round((completed_goals / total_goals * 100), 1) if total_goals > 0 else 0

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


def about_view(request):
    return render(request, 'core/about.html')
