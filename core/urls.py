from django.urls import path

from . import views


urlpatterns = []

GENERAL_URLS = [
    path('', views.index, name='index'),
    path('categories/', views.category_list, name='category_list'),
    path('domain/<int:domain_id>/tracks/', views.domain_tracks_view, name='domain_tracks'),
    path('domain/<int:domain_id>/track/<int:track_id>/goals/', views.track_goals_view, name='track_goals'),
    path('goal/<int:goal_id>/edit/', views.edit_goal_view, name='edit_goal'),
    path('goal/<int:goal_id>/delete/', views.delete_goal_view, name='delete_goal'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('goal/<int:goal_id>/toggle-complete/', views.toggle_complete_goal_view, name='toggle_complete_goal'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.faq_view, name='faq'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('support/', views.support_view, name='support'),
    path('supervisor/students/', views.supervisor_students_list_view, name='supervisor_students_list'),
    path('supervisor/students/<int:student_id>/', views.supervisor_student_detail_view, name='supervisor_student_detail'),
    path('camps/', views.camp_list_view, name='camp_list'),
    path('camp/<int:camp_id>/', views.camp_detail_view, name='camp_detail'),
    path('goals/<int:goal_id>/', views.goal_detail_view, name='goal_detail'),
    path('comments/<int:comment_id>/edit/', views.edit_comment_view, name='edit_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment_view, name='delete_comment'),
]

APIS_URLS = []

urlpatterns = GENERAL_URLS + APIS_URLS