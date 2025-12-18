from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, FileExtensionValidator
from django.utils import timezone
import os
import jdatetime

def user_profile_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'profile_{instance.username}_{instance.id}.{ext}'
    return os.path.join('profile_images', filename)

class CustomUser(AbstractUser):
    AGE_GROUP_CHOICES = (
        ('under_7', 'زیر ۷ سال'),
        ('7_15', '۷ تا ۱۵ سال'),
        ('15_25', '۱۵ تا ۲۵ سال'),
        ('over_25', 'بالای ۲۵ سال'),
    )
    
    USER_TYPE_CHOICES = (
        ('normal', 'کاربر عادی'),
        ('worker', 'کارگر'),
        ('employee', 'کارمند'),
    )
    
    national_code = models.CharField(
        max_length=10,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[0-9]{10}$',
                message='کد ملی باید ۱۰ رقم باشد'
            )
        ],
        verbose_name='کد ملی'
    )
    
    profile_image = models.ImageField(
        upload_to=user_profile_image_path,
        blank=True,
        null=True,
        verbose_name='عکس پروفایل',
        default='profile_images/default_profile.jpg'
    )
    
    age_group = models.CharField(
        max_length=10,
        choices=AGE_GROUP_CHOICES,
        verbose_name='گروه سنی',
        blank=True,
        null=True
    )
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='normal',
        verbose_name='نوع کاربر'
    )
    
    address = models.TextField(blank=True, null=True, verbose_name='آدرس')
    job_document = models.FileField(
        upload_to='documents/',
        blank=True,
        null=True,
        verbose_name='مستند شغلی',
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'])
        ]
    )
    
    phone_number = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex='^09[0-9]{9}$',
                message='شماره موبایل باید با 09 شروع شود و 11 رقم باشد'
            )
        ],
        verbose_name='شماره موبایل'
    )
    
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاریخ تولد'
    )
    
    bio = models.TextField(blank=True, null=True, verbose_name='درباره من', max_length=500)
    website = models.URLField(blank=True, null=True, verbose_name='وبسایت')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین به‌روزرسانی')
    
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.national_code}"
    
    def get_age_group_display_name(self):
        return dict(self.AGE_GROUP_CHOICES).get(self.age_group, 'نامشخص')
    
    def get_user_type_display_name(self):
        return dict(self.USER_TYPE_CHOICES).get(self.user_type, 'نامشخص')
    
    def calculate_age(self):
        if self.birth_date:
            today = timezone.now().date()
            age = today.year - self.birth_date.year
            if today.month < self.birth_date.month or (today.month == self.birth_date.month and today.day < self.birth_date.day):
                age -= 1
            return age
        return None
    
    def get_profile_image_url(self):
        if self.profile_image and hasattr(self.profile_image, 'url') and self.profile_image.name:
            try:
                return self.profile_image.url
            except:
                pass
        return '/static/images/default_profile.jpg'
    
    def get_birth_date_jalali(self):
        if self.birth_date:
            jalali_date = jdatetime.date.fromgregorian(date=self.birth_date)
            return jalali_date.strftime('%Y/%m/%d')
        return ''
    
    def save(self, *args, **kwargs):
        if self.birth_date and not self.age_group:
            age = self.calculate_age()
            if age is not None:
                if age < 7:
                    self.age_group = 'under_7'
                elif 7 <= age < 15:
                    self.age_group = '7_15'
                elif 15 <= age < 25:
                    self.age_group = '15_25'
                else:
                    self.age_group = 'over_25'
        super().save(*args, **kwargs)

class ContactMessage(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در انتظار'),
        ('read', 'خوانده شده'),
        ('replied', 'پاسخ داده شده'),
    )
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        verbose_name='کاربر',
        related_name='contact_messages'
    )
    
    subject = models.CharField(max_length=200, verbose_name='موضوع')
    message = models.TextField(verbose_name='پیام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    admin_response = models.TextField(blank=True, null=True, verbose_name='پاسخ ادمین')
    responded_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ پاسخ')
    
    class Meta:
        verbose_name = 'پیام تماس'
        verbose_name_plural = 'پیام‌های تماس'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.subject}"
    
    def save(self, *args, **kwargs):
        if self.admin_response and not self.responded_at:
            self.responded_at = timezone.now()
            self.status = 'replied'
        super().save(*args, **kwargs)
    
    def get_created_at_jalali(self):
        if self.created_at:
            jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.created_at)
            return jalali_datetime.strftime('%Y/%m/%d - %H:%M')
        return ''

class UserMessage(models.Model):
    MESSAGE_TYPE_CHOICES = (
        ('contact', 'پیام تماس'),
        ('response', 'پاسخ ادمین'),
        ('private', 'پیام خصوصی'),
    )
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        verbose_name='کاربر',
        related_name='user_messages'
    )
    
    contact_message = models.ForeignKey(
        ContactMessage, 
        on_delete=models.CASCADE, 
        verbose_name='پیام تماس', 
        null=True, 
        blank=True,
        related_name='user_responses'
    )
    
    is_from_admin = models.BooleanField(default=False, verbose_name='از طرف ادمین')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='contact', verbose_name='نوع پیام')
    subject = models.CharField(max_length=200, verbose_name='موضوع')
    content = models.TextField(verbose_name='محتوا')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
    
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        verbose_name='فرستنده',
        null=True,
        blank=True,
        related_name='sent_user_messages'
    )
    
    class Meta:
        verbose_name = 'پیام کاربر'
        verbose_name_plural = 'پیام‌های کاربران'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_from_admin']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.subject}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])
    
    def get_sender_name(self):
        if self.is_from_admin:
            return "ادمین سیستم"
        elif self.sender:
            return self.sender.get_full_name() or self.sender.username
        return "سیستم"
    
    def get_created_at_jalali(self):
        if self.created_at:
            jalali_datetime = jdatetime.datetime.fromgregorian(datetime=self.created_at)
            return jalali_datetime.strftime('%Y/%m/%d - %H:%M')
        return ''
    
    def save(self, *args, **kwargs):
        if self.is_from_admin and not self.sender:
            admin_user = CustomUser.objects.filter(is_staff=True).first()
            if admin_user:
                self.sender = admin_user
        super().save(*args, **kwargs)