from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ContactMessage, UserMessage

@receiver(post_save, sender=ContactMessage)
def create_user_message_on_admin_response(sender, instance, created, **kwargs):
    """هنگامی که ادمین به پیام تماس پاسخ داد، پیامی برای کاربر ایجاد کن"""
    if not created and instance.admin_response and instance.status == 'replied':
        # بررسی کن که آیا قبلاً پیامی برای این پاسخ ایجاد شده یا نه
        existing_message = UserMessage.objects.filter(
            contact_message=instance,
            is_from_admin=True
        ).exists()
        
        if not existing_message:
            # ایجاد پیام برای کاربر
            UserMessage.objects.create(
                user=instance.user,
                contact_message=instance,
                is_from_admin=True,
                message_type='response',
                subject=f"پاسخ: {instance.subject}",
                content=instance.admin_response,
                sender=None,  # ادمین سیستم
                receiver=instance.user,
                is_read=False
            )