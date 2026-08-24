from django.urls import path

from . import views


urlpatterns = []

GENERAL_URLS = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]

APIS_URLS = []

urlpatterns = GENERAL_URLS + APIS_URLS