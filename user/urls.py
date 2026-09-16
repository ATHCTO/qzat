from django.urls import path

from user.views import profile_views, create_user, auth_views

urlpatterns = []

GENERAL_URLS = [
    path('login/', auth_views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', profile_views.profile_view, name='profile'),
    path('admin-panel/create-user/', create_user.create_user_by_admin, name='create_user'),
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='user/password_change.html',
        success_url='/password-change/done/'
    ), name='password_change'),

    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='user/password_change_done.html'
    ), name='password_change_done'),
]

APIS_URLS = []

urlpatterns = GENERAL_URLS + APIS_URLS