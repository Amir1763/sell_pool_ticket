from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
import jdatetime
from .models import CustomUser, ContactMessage, UserMessage

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 
                   'national_code', 'age_group', 'user_type', 
                   'is_staff', 'is_active', 'profile_image_preview',
                   'get_created_at_jalali')
    list_filter = ('user_type', 'age_group', 'is_staff', 'is_active', 'created_at')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('اطلاعات شخصی', {'fields': (
            'first_name', 'last_name', 'email', 'national_code',
            'profile_image', 'profile_image_preview', 'age_group',
            'phone_number', 'birth_date', 'bio', 'website'
        )}),
        ('اطلاعات شغلی', {'fields': ('user_type', 'address', 'job_document')}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_staff', 
                                 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2',
                      'first_name', 'last_name', 'national_code', 
                      'age_group', 'user_type')}
        ),
    )
    
    readonly_fields = ('profile_image_preview', 'created_at', 'updated_at', 'date_joined', 'last_login')
    
    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.profile_image.url)
        return format_html('<div style="width: 50px; height: 50px; border-radius: 50%; background: #667eea; color: white; display: flex; align-items: center; justify-content: center;">{}{}</div>', 
                          obj.first_name[0] if obj.first_name else '', 
                          obj.last_name[0] if obj.last_name else '')
    
    profile_image_preview.short_description = 'پروفایل'
    
    def get_created_at_jalali(self, obj):
        if obj.created_at:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
            return jalali_date.strftime('%Y/%m/%د - %H:%M')
        return '-'
    
    get_created_at_jalali.short_description = 'تاریخ عضویت'
    get_created_at_jalali.admin_order_field = 'created_at'
    
    search_fields = ('username', 'email', 'first_name', 'last_name', 'national_code', 'phone_number')
    ordering = ('-created_at',)

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'status', 'get_created_at_jalali', 'get_responded_at_jalali')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'subject', 'message')
    readonly_fields = ('user', 'subject', 'message', 'created_at', 'responded_at')
    fieldsets = (
        ('اطلاعات پیام', {
            'fields': ('user', 'subject', 'message', 'created_at', 'status')
        }),
        ('پاسخ ادمین', {
            'fields': ('admin_response', 'responded_at')
        }),
    )
    
    def get_created_at_jalali(self, obj):
        if obj.created_at:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
            return jalali_date.strftime('%Y/%m/%د - %H:%M')
        return '-'
    
    get_created_at_jalali.short_description = 'تاریخ ارسال'
    get_created_at_jalali.admin_order_field = 'created_at'
    
    def get_responded_at_jalali(self, obj):
        if obj.responded_at:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.responded_at)
            return jalali_date.strftime('%Y/%m/%د - %H:%M')
        return '-'
    
    get_responded_at_jalali.short_description = 'تاریخ پاسخ'
    get_responded_at_jalali.admin_order_field = 'responded_at'
    
    def save_model(self, request, obj, form, change):
        if obj.admin_response and not obj.responded_at:
            obj.status = 'replied'
        super().save_model(request, obj, form, change)

class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'is_from_admin', 'is_read', 'get_created_at_jalali')
    list_filter = ('is_from_admin', 'is_read', 'created_at')
    search_fields = ('user__username', 'subject', 'content')
    
    def get_created_at_jalali(self, obj):
        if obj.created_at:
            jalali_date = jdatetime.datetime.fromgregorian(datetime=obj.created_at)
            return jalali_date.strftime('%Y/%m/%د - %H:%M')
        return '-'
    
    get_created_at_jalali.short_description = 'تاریخ ارسال'
    get_created_at_jalali.admin_order_field = 'created_at'

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ContactMessage, ContactMessageAdmin)
admin.site.register(UserMessage, UserMessageAdmin)