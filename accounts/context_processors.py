from django.db.models import Q
from .models import UserMessage
import jdatetime

def unread_messages_count(request):
    """شمارش پیام‌های خوانده نشده برای نمایش در navbar"""
    if request.user.is_authenticated and not request.user.is_anonymous:
        try:
            unread_count = UserMessage.objects.filter(
                Q(user=request.user) | Q(receiver=request.user),
                is_read=False,
                is_from_admin=True
            ).distinct().count()
            return {'user_messages_unread': unread_count}
        except:
            return {'user_messages_unread': 0}
    return {'user_messages_unread': 0}


def user_info(request):
    """اطلاعات کاربر برای نمایش در navbar"""
    if request.user.is_authenticated and not request.user.is_anonymous:
        try:
            # تعداد کل پیام‌های کاربر
            total_messages = UserMessage.objects.filter(
                Q(user=request.user) | Q(receiver=request.user)
            ).distinct().count()
            
            # پیام‌های اخیر
            recent_messages = UserMessage.objects.filter(
                Q(user=request.user) | Q(receiver=request.user)
            ).distinct().order_by('-created_at')[:5]
            
            return {
                'user_total_messages': total_messages,
                'user_recent_messages': recent_messages,
                'user_profile_image_url': request.user.get_profile_image_url() if hasattr(request.user, 'get_profile_image_url') else '',
            }
        except:
            return {
                'user_total_messages': 0,
                'user_recent_messages': [],
                'user_profile_image_url': '',
            }
    
    return {
        'user_total_messages': 0,
        'user_recent_messages': [],
        'user_profile_image_url': '',
    }

def jalali_filters(request):
    """اضافه کردن فیلترهای تاریخ شمسی به context"""
    def to_jalali(value):
        if not value:
            return ''
        try:
            if hasattr(value, 'hour'):
                jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
                return jalali_date.strftime('%Y/%m/%د - %H:%M')
            else:
                jalali_date = jdatetime.date.fromgregorian(date=value)
                return jalali_date.strftime('%Y/%m/%د')
        except:
            return str(value)
    
    def jalali_date(value, format_str='%Y/%m/%د'):
        if not value:
            return ''
        try:
            if hasattr(value, 'hour'):
                jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
            else:
                jalali_date = jdatetime.date.fromgregorian(date=value)
            return jalali_date.strftime(format_str)
        except:
            return str(value)
    
    return {
        'to_jalali': to_jalali,
        'jalali_date': jalali_date,
    }