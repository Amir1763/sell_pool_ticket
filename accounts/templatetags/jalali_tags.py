from django import template
import jdatetime
from django.utils import timezone

register = template.Library()

@register.filter
def to_jalali(value):
    """تبدیل تاریخ میلادی به هجری شمسی"""
    if not value:
        return ''
    
    try:
        # اگر تاریخ دارای زمان باشد
        if hasattr(value, 'hour'):
            jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
            return jalali_date.strftime('%Y/%m/%d - %H:%M')
        else:
            # فقط تاریخ
            jalali_date = jdatetime.date.fromgregorian(date=value)
            return jalali_date.strftime('%Y/%m/%d')
    except:
        return str(value)


@register.filter
def jalali_date(value, format_str='%Y/%m/%d'):
    """فرمت‌دهی تاریخ هجری شمسی"""
    if not value:
        return ''
    
    try:
        if isinstance(value, str):
            # اگر رشته است، فرض می‌کنیم تاریخ میلادی است
            if hasattr(value, 'hour'):
                jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
            else:
                jalali_date = jdatetime.date.fromgregorian(date=value)
        else:
            # اگر شیء تاریخ است
            if hasattr(value, 'hour'):
                jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
            else:
                jalali_date = jdatetime.date.fromgregorian(date=value)
        
        return jalali_date.strftime(format_str)
    except:
        return str(value)


@register.filter
def jalali_datetime(value, format_str='%Y/%m/%d - %H:%M'):
    """فرمت‌دهی تاریخ و زمان هجری شمسی"""
    return jalali_date(value, format_str)


@register.filter
def jalali_time(value, format_str='%H:%M'):
    """فرمت‌دهی زمان هجری شمسی"""
    if not value:
        return ''
    
    try:
        jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        return jalali_date.strftime(format_str)
    except:
        return str(value)


@register.simple_tag
def jalali_now(format_str='%Y/%m/%د - %H:%M:%S'):
    """دریافت تاریخ و زمان فعلی به هجری شمسی"""
    now = timezone.now()
    jalali_now = jdatetime.datetime.fromgregorian(datetime=now)
    return jalali_now.strftime(format_str)


@register.filter
def jalali_year(value):
    """دریافت سال هجری شمسی"""
    if not value:
        return ''
    
    try:
        if hasattr(value, 'hour'):
            jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        else:
            jalali_date = jdatetime.date.fromgregorian(date=value)
        return jalali_date.year
    except:
        return ''


@register.filter
def jalali_month(value):
    """دریافت ماه هجری شمسی"""
    if not value:
        return ''
    
    try:
        if hasattr(value, 'hour'):
            jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        else:
            jalali_date = jdatetime.date.fromgregorian(date=value)
        return jalali_date.month
    except:
        return ''


@register.filter
def jalali_month_name(value):
    """دریافت نام ماه هجری شمسی"""
    if not value:
        return ''
    
    try:
        if hasattr(value, 'hour'):
            jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        else:
            jalali_date = jdatetime.date.fromgregorian(date=value)
        
        month_names = {
            1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد',
            4: 'تیر', 5: 'مرداد', 6: 'شهریور',
            7: 'مهر', 8: 'آبان', 9: 'آذر',
            10: 'دی', 11: 'بهمن', 12: 'اسفند'
        }
        
        return month_names.get(jalali_date.month, '')
    except:
        return ''


@register.filter
def jalali_day(value):
    """دریافت روز هجری شمسی"""
    if not value:
        return ''
    
    try:
        if hasattr(value, 'hour'):
            jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        else:
            jalali_date = jdatetime.date.fromgregorian(date=value)
        return jalali_date.day
    except:
        return ''


@register.filter
def jalali_weekday_name(value):
    """دریافت نام روز هفته هجری شمسی"""
    if not value:
        return ''
    
    try:
        if hasattr(value, 'hour'):
            jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        else:
            jalali_date = jdatetime.date.fromgregorian(date=value)
        
        weekday_names = {
            0: 'شنبه', 1: 'یکشنبه', 2: 'دوشنبه',
            3: 'سه‌شنبه', 4: 'چهارشنبه', 5: 'پنجشنبه',
            6: 'جمعه'
        }
        
        return weekday_names.get(jalali_date.weekday(), '')
    except:
        return ''


@register.simple_tag
def jalali_calendar(year=None, month=None):
    """ایجاد تقویم هجری شمسی"""
    now = jdatetime.datetime.now()
    if not year:
        year = now.year
    if not month:
        month = now.month
    
    return {
        'year': year,
        'month': month,
        'month_name': jalali_month_name(now),
        'now': now
    }

@register.filter
def get_item(dictionary, key):
    """دریافت مقدار از دیکشنری با استفاده از کلید"""
    if dictionary and key in dictionary:
        return dictionary[key]
    return None