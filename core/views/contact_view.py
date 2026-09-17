from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail

import requests

from core.models.contact import ContactMessage


def contact_view(request):
    if request.method == 'POST':
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': getattr(settings, 'RECAPTCHA_SECRET_KEY', 'YOUR_RECAPTCHA_SECRET_KEY'),
            'response': recaptcha_response
        }
        
        try:
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data, timeout=5)
            result = r.json()
        except requests.exceptions.RequestException:
            messages.error(request, 'تعذر التحقق من الكابتشا، يرجى المحاولة لاحقاً.')
            return redirect('contact')

        if not result.get('success'):
            messages.error(request, 'يرجى تأكيد أنك لست برنامج روبوت (reCAPTCHA).')
            return redirect('contact')

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not all([name, email, subject, message]):
            messages.error(request, 'جميع الحقول مطلوبة، يرجى إعادة المحاولة.')
            return redirect('contact')

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        email_body = f"رسالة جديدة من: {name}\nالبريد: {email}\nالموضوع: {subject}\n\nالنص:\n{message}"
        try:
            send_mail(
                subject=f"تواصل جديد: {subject}",
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, 'تم إرسال رسالتك بنجاح! سنقوم بالتواصل معك في أقرب وقت.')
        return redirect('contact')

    return render(request, 'core/contact.html')

