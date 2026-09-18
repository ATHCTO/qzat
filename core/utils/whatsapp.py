import requests
from django.conf import settings

def send_whatsapp_message(phone_number, message_text):
    """
    إرسال رسالة واتساب عبر Green API
    """
    if not phone_number:
        return False

    # تنظيف الرقم من أي رموز زائدة
    clean_phone = ''.join(filter(str.isdigit, str(phone_number)))
    
    # صيغة chatId المطلوبة لـ Green API
    chat_id = f"{clean_phone}@c.us"

    # جلب الإعدادات بناءً على أسمائها في settings.py
    base_url = settings.GREENAPI_URL
    id_instance = settings.GREENAPI_ID_INSTANCE
    api_token = settings.GREENAPI_API_TOKEN_INSTANCE

    # التأكد من وجود جميع الإعدادات المطلوبة
    if not all([base_url, id_instance, api_token]):
        print("خطأ: إعدادات Green API غير مكتملة في settings.py أو .env")
        return False

    # تكوين الرابط الكامل لإرسال الرسالة
    url = f"{base_url.rstrip('/')}/waInstance{id_instance}/sendMessage/{api_token}"

    payload = {
        "chatId": chat_id,
        "message": message_text
    }
    
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"خطأ أثناء إرسال رسالة Green API: {e}")
        return False