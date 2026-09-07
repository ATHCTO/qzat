from django.urls import path

from core.views import index_view, category_view, domain_view, goal_view, comment_view, supervisor_view, contact_view, camp_view

urlpatterns = []

GENERAL_URLS = [
    path('', index_view.index_view, name='index'),
    path('categories/', category_view.category_list, name='category_list'),
    path('domain/<int:domain_id>/tracks/', domain_view.domain_tracks_view, name='domain_tracks'),
    path('domain/<int:domain_id>/track/<int:track_id>/goals/', goal_view.track_goals_view, name='track_goals'),
    path('goal/<int:goal_id>/edit/', goal_view.edit_goal_view, name='edit_goal'),
    path('goal/<int:goal_id>/delete/', goal_view.delete_goal_view, name='delete_goal'),
    path('dashboard/', index_view.dashboard_view, name='dashboard'),
    path('goal/<int:goal_id>/toggle-complete/', goal_view.toggle_complete_goal_view, name='toggle_complete_goal'),
    path('about/', index_view.about_view, name='about'),
    path('contact/', contact_view.contact_view, name='contact'),
    path('faq/', index_view.faq_view, name='faq'),
    path('privacy/', index_view.privacy_view, name='privacy'),
    path('support/', index_view.support_view, name='support'),
    path('supervisor/students/', supervisor_view.supervisor_students_list_view, name='supervisor_students_list'),
    path('supervisor/students/<int:student_id>/', supervisor_view.supervisor_student_detail_view, name='supervisor_student_detail'),
    path('camps/', camp_view.camp_list_view, name='camp_list'),
    path('camp/<int:camp_id>/', camp_view.camp_detail_view, name='camp_detail'),
    path('goals/<int:goal_id>/', goal_view.goal_detail_view, name='goal_detail'),
    path('comments/<int:comment_id>/edit/', comment_view.edit_comment_view, name='edit_comment'),
    path('comments/<int:comment_id>/delete/', comment_view.delete_comment_view, name='delete_comment'),
]

APIS_URLS = []

urlpatterns = GENERAL_URLS + APIS_URLS