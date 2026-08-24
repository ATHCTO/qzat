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
]

APIS_URLS = []

urlpatterns = GENERAL_URLS + APIS_URLS