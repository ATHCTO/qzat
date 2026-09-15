from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView


class CustomLoginView(LoginView):
    template_name = 'user/login.html'
    redirect_authenticated_user = True
    def form_invalid(self, form):
        messages.error(
            self.request,
            'اسم المستخدم أو كلمة المرور غير صحيحة.'
        )
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    template_name = 'user/logout.html'
    redirect_authenticated_user = True