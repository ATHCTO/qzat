import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')

# تحميل الإعدادات من settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# تطبيق خيارات البروتوكول المباشر لمنع أمر HELLO
app.conf.broker_transport_options = {'protocol_version': 2}
app.conf.result_backend_transport_options = {'protocol_version': 2}

app.autodiscover_tasks()