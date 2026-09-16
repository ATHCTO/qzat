from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.exempt_urls = [
            reverse('login'),
            reverse('logout'),
        ]
        
    def __call__(self, request):
        if request.path == settings.LOGIN_URL:
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)