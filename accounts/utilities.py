import jdatetime
from django.utils import timezone
from django import template

register = template.Library()

def gregorian_to_jalali(gregorian_date):
    """تبدیل تاریخ میلادی به هجری شمسی"""
    if not gregorian_date:
        return ''
    
    # اگر تاریخ دارای زمان باشد
    if hasattr(gregorian_date, 'hour'):
        jalali_date = jdatetime.datetime.fromgregorian(
            year=gregorian_date.year,
            month=gregorian_date.month,
            day=gregorian_date.day,
            hour=gregorian_date.hour,
            minute=gregorian_date.minute,
            second=gregorian_date.second
        )
        return jalali_date.strftime('%Y/%m/%d - %H:%M')
    else:
        # فقط تاریخ
        jalali_date = jdatetime.date.fromgregorian(
            year=gregorian_date.year,
            month=gregorian_date.month,
            day=gregorian_date.day
        )
        return jalali_date.strftime('%Y/%m/%d')


def jalali_to_gregorian(jalali_date_str):
    """تبدیل تاریخ هجری شمسی به میلادی (برای فرم‌ها)"""
    if not jalali_date_str:
        return None
    
    try:
        jalali_date = jdatetime.datetime.strptime(jalali_date_str, '%Y/%m/%d')
        gregorian_date = jalali_date.togregorian()
        return gregorian_date
    except:
        return None


def get_jalali_now():
    """دریافت تاریخ و زمان فعلی به هجری شمسی"""
    now = timezone.now()
    jalali_now = jdatetime.datetime.fromgregorian(datetime=now)
    return jalali_now


def format_jalali_date(date_obj, format_str='%Y/%m/%d'):
    """فرمت‌دهی تاریخ هجری شمسی"""
    if not date_obj:
        return ''
    
    if isinstance(date_obj, jdatetime.datetime) or isinstance(date_obj, jdatetime.date):
        return date_obj.strftime(format_str)
    
    # اگر تاریخ میلادی است، ابتدا تبدیل کن
    if hasattr(date_obj, 'year'):
        if hasattr(date_obj, 'hour'):
            jalali_date = jdatetime.datetime.fromgregorian(
                year=date_obj.year,
                month=date_obj.month,
                day=date_obj.day,
                hour=date_obj.hour,
                minute=date_obj.minute,
                second=date_obj.second
            )
        else:
            jalali_date = jdatetime.date.fromgregorian(
                year=date_obj.year,
                month=date_obj.month,
                day=date_obj.day
            )
        return jalali_date.strftime(format_str)
    
    return ''


# فیلترهای تمپلیت
@register.filter
def to_jalali(value):
    """فیلتر تمپلیت برای تبدیل تاریخ به هجری شمسی"""
    return gregorian_to_jalali(value)


@register.filter
def jalali_date(value, format_str='%Y/%m/%d'):
    """فیلتر تمپلیت برای فرمت‌دهی تاریخ هجری شمسی"""
    return format_jalali_date(value, format_str)


@register.filter
def jalali_datetime(value, format_str='%Y/%m/%d - %H:%M'):
    """فیلتر تمپلیت برای فرمت‌دهی تاریخ و زمان هجری شمسی"""
    return format_jalali_date(value, format_str)


@register.filter
def jalali_year(value):
    """فیلتر تمپلیت برای دریافت سال هجری شمسی"""
    if not value:
        return ''
    
    if hasattr(value, 'year'):
        if hasattr(value, 'hour'):
            jalali_date = jdatetime.datetime.fromgregorian(
                year=value.year,
                month=value.month,
                day=value.day
            )
        else:
            jalali_date = jdatetime.date.fromgregorian(
                year=value.year,
                month=value.month,
                day=value.day
            )
        return jalali_date.year
    
    return ''


@register.filter
def jalali_month_name(value):
    """فیلتر تمپلیت برای دریافت نام ماه هجری شمسی"""
    if not value:
        return ''
    
    if hasattr(value, 'year'):
        if hasattr(value, 'hour'):
            jalali_date = jdatetime.datetime.fromgregorian(
                year=value.year,
                month=value.month,
                day=value.day
            )
        else:
            jalali_date = jdatetime.date.fromgregorian(
                year=value.year,
                month=value.month,
                day=value.day
            )
        
        month_names = {
            1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد',
            4: 'تیر', 5: 'مرداد', 6: 'شهریور',
            7: 'مهر', 8: 'آبان', 9: 'آذر',
            10: 'دی', 11: 'بهمن', 12: 'اسفند'
        }
        
        return month_names.get(jalali_date.month, '')
    
    return ''