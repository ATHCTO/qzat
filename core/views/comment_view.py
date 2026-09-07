from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from core.models import GoalComment


@login_required(login_url='login')
def edit_comment_view(request, comment_id):
    comment = get_object_or_404(GoalComment, id=comment_id)
    
    if comment.user != request.user:
        messages.error(request, 'عفواً، يمكنك تعديل تعليقاتك الخاصة فقط!')
        return redirect('goal_detail', goal_id=comment.goal.id)

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

    if comment.user != request.user:
        messages.error(request, 'عفواً، يمكنك حذف تعليقاتك الخاصة فقط!')
        return redirect('goal_detail', goal_id=goal_id)

    if not comment.is_editable():
        messages.error(request, 'عفواً، انتهت المهلة المحددة (ساعة واحدة) لحذف هذا التعليق!')
        return redirect('goal_detail', goal_id=goal_id)

    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'تم حذف التعليق بنجاح!')

    return redirect('goal_detail', goal_id=goal_id)