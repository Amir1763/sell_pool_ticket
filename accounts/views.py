from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from .forms import (
    CustomUserCreationForm, LoginForm, ProfileUpdateForm, 
    ContactForm, AdminResponseForm, AdminToUserMessageForm,
    UserToAdminMessageForm, UserTypeUpdateForm
)
from .models import CustomUser, ContactMessage, UserMessage
import logging
import os

logger = logging.getLogger(__name__)

def is_admin(user):
    return user.is_staff

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'ثبت‌نام با موفقیت انجام شد!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'ورود موفقیت‌آمیز بود!')
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'با موفقیت خارج شدید!')
    return redirect('login')

@login_required
def home_view(request):
    return render(request, 'home/home.html')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'پروفایل با موفقیت به‌روزرسانی شد!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'user_type_display': dict(CustomUser.USER_TYPE_CHOICES).get(request.user.user_type)
    }
    return render(request, 'accounts/profile.html', context)

@login_required
@user_passes_test(is_admin)
def dashboard_view(request):
    user_stats = {
        'total': CustomUser.objects.count(),
        'normal': CustomUser.objects.filter(user_type='normal').count(),
        'worker': CustomUser.objects.filter(user_type='worker').count(),
        'employee': CustomUser.objects.filter(user_type='employee').count(),
    }
    
    # پیام‌های تماس
    contact_messages = ContactMessage.objects.all().order_by('-created_at')
    pending_contact_messages = contact_messages.filter(status='pending')
    

    # پیام‌های شخصی کاربران به ادمین
    private_messages = UserMessage.objects.filter(
        is_from_admin=False,
        message_type='private'
    ).order_by('-created_at')
    
    pending_private_messages = private_messages.filter(is_read=False)
    

    # صفحه‌بندی پیام‌های تماس
    contact_paginator = Paginator(contact_messages, 10)
    contact_page_number = request.GET.get('contact_page')
    contact_page_obj = contact_paginator.get_page(contact_page_number)


        # صفحه‌بندی پیام‌های شخصی
    private_paginator = Paginator(private_messages, 10)
    private_page_number = request.GET.get('private_page')
    private_page_obj = private_paginator.get_page(private_page_number)


    context = {
        'user_stats': user_stats,
        'contact_messages': contact_page_obj,
        'private_messages': private_page_obj,
        'pending_contact_count': pending_contact_messages.count(),
        'pending_private_count': pending_private_messages.count(),
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                contact_message = ContactMessage.objects.create(
                    user=request.user,
                    subject=form.cleaned_data['subject'],
                    message=form.cleaned_data['message'],
                    status='pending'
                )
                
                UserMessage.objects.create(
                    user=request.user,
                    contact_message=contact_message,
                    is_from_admin=False,
                    message_type='contact',
                    subject=form.cleaned_data['subject'],
                    content=form.cleaned_data['message'],
                    sender=request.user,
                    is_read=True
                )
                
                logger.info(f"پیام تماس جدید از کاربر {request.user.username}")
                messages.success(request, 'پیام شما با موفقیت ارسال شد!')
                return redirect('contact')
            except Exception as e:
                logger.error(f"خطا در ارسال پیام تماس: {str(e)}")
                messages.error(request, 'خطا در ارسال پیام. لطفاً مجدداً تلاش کنید.')
    else:
        form = ContactForm()
    
    return render(request, 'home/callus.html', {'form': form})

def about_view(request):
    return render(request, 'home/aboutme.html')

@login_required
def send_private_message_view(request):
    if request.method == 'POST':
        form = UserToAdminMessageForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                message = form.save()
                logger.info(f"پیام خصوصی جدید از کاربر {request.user.username} ارسال شد: {message.id}")
                messages.success(request, 'پیام شما با موفقیت ارسال شد!')
                return redirect('my_messages')
            except Exception as e:
                logger.error(f"خطا در ارسال پیام خصوصی: {str(e)}")
                messages.error(request, 'خطا در ارسال پیام. لطفاً مجدداً تلاش کنید.')
    else:
        form = UserToAdminMessageForm(user=request.user)
    
    return render(request, 'accounts/send_private_message.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def respond_message_view(request, message_id):
    contact_message = get_object_or_404(ContactMessage, id=message_id)
    
    if request.method == 'POST':
        form = AdminResponseForm(request.POST, instance=contact_message)
        if form.is_valid():
            try:
                contact_message = form.save(commit=False)
                contact_message.status = 'replied'
                contact_message.responded_at = timezone.now()
                contact_message.save()
                
                UserMessage.objects.create(
                    user=contact_message.user,
                    contact_message=contact_message,
                    is_from_admin=True,
                    message_type='response',
                    subject=f"پاسخ به: {contact_message.subject}",
                    content=form.cleaned_data['admin_response'],
                    sender=request.user,
                    is_read=False
                )
                
                logger.info(f"پاسخ ادمین به پیام {contact_message.id} ارسال شد")
                messages.success(request, 'پاسخ با موفقیت ارسال شد!')
                return redirect('dashboard')
            except Exception as e:
                logger.error(f"خطا در ارسال پاسخ: {str(e)}")
                messages.error(request, 'خطا در ارسال پاسخ. لطفاً مجدداً تلاش کنید.')
    else:
        form = AdminResponseForm(instance=contact_message)
    
    return render(request, 'accounts/respond_message.html', {
        'form': form,
        'message': contact_message
    })

@login_required
@user_passes_test(is_admin)
def respond_private_message_view(request, message_id):
    """پاسخ ادمین به پیام خصوصی کاربر"""
    user_message = get_object_or_404(UserMessage, id=message_id, is_from_admin=False)
    
    if request.method == 'POST':
        subject = request.POST.get('subject', f"پاسخ به: {user_message.subject}")
        content = request.POST.get('content')
        
        if content:
            try:
                # ایجاد پاسخ از ادمین
                response_message = UserMessage.objects.create(
                    user=user_message.user,
                    is_from_admin=True,
                    message_type='private',
                    subject=subject,
                    content=content,
                    sender=request.user,
                    is_read=False
                )
                
                logger.info(f"پاسخ ادمین به پیام خصوصی {user_message.id} ارسال شد")
                messages.success(request, 'پاسخ با موفقیت ارسال شد!')
                return redirect('dashboard')
            except Exception as e:
                logger.error(f"خطا در ارسال پاسخ به پیام خصوصی: {str(e)}")
                messages.error(request, 'خطا در ارسال پاسخ. لطفاً مجدداً تلاش کنید.')
        else:
            messages.error(request, 'لطفاً متن پاسخ را وارد کنید.')
    
    return render(request, 'accounts/respond_private_message.html', {
        'message': user_message
    })



@login_required
def my_messages_view(request):
    """نمایش پیام‌های کاربر"""
    try:
        # پیام‌های دریافتی کاربر (از ادمین)
        received_messages = UserMessage.objects.filter(
            user=request.user,
            is_from_admin=True
        ).order_by('-created_at')
        
        # پیام‌های ارسالی کاربر (به ادمین)
        sent_messages = UserMessage.objects.filter(
            user=request.user,
            is_from_admin=False
        ).order_by('-created_at')
        
        # پیام‌های تماس کاربر با پاسخ ادمین
        contact_messages = ContactMessage.objects.filter(
            user=request.user
        ).order_by('-created_at')
        
        # برای هر پیام تماس، پیام اصلی (اولیه) را پیدا کن
        original_messages_dict = {}
        for contact_msg in contact_messages:
            # پیدا کردن اولین UserMessage مرتبط با این ContactMessage
            first_user_message = UserMessage.objects.filter(
                contact_message=contact_msg,
                is_from_admin=False
            ).first()
            if first_user_message:
                original_messages_dict[contact_msg.id] = first_user_message
        
        # ترکیب تمام پیام‌ها برای نمایش یکپارچه
        all_messages = list(received_messages) + list(sent_messages)
        all_messages.sort(key=lambda x: x.created_at, reverse=True)
        
        # شمارش پیام‌های خوانده نشده
        unread_count = received_messages.filter(is_read=False).count()
        
        # صفحه‌بندی تمام پیام‌ها
        all_paginator = Paginator(all_messages, 15)
        all_page_number = request.GET.get('page')
        all_page_obj = all_paginator.get_page(all_page_number)
        
        context = {
            'all_messages': all_page_obj,
            'received_messages': received_messages,
            'sent_messages': sent_messages,
            'contact_messages': contact_messages,
            'original_messages_dict': original_messages_dict,  # اضافه کردن این خط
            'unread_count': unread_count,
            'total_received': received_messages.count(),
            'total_sent': sent_messages.count(),
            'total_all': len(all_messages),
        }
        
        logger.info(f"نمایش پیام‌های کاربر {request.user.username} - تعداد: {len(all_messages)}")
        return render(request, 'accounts/my_messages.html', context)
        
    except Exception as e:
        logger.error(f"خطا در نمایش پیام‌های کاربر: {str(e)}")
        messages.error(request, 'خطا در بارگذاری پیام‌ها.')
        return render(request, 'accounts/my_messages.html', {
            'all_messages': [],
            'received_messages': [],
            'sent_messages': [],
            'contact_messages': [],
            'original_messages_dict': {},
            'unread_count': 0,
            'total_received': 0,
            'total_sent': 0,
            'total_all': 0,
        })
    
@login_required
def view_my_message_detail(request, message_id):
    """نمایش جزئیات یک پیام"""
    try:
        # پیدا کردن پیام (هم پیام‌های دریافتی و هم ارسالی)
        message = get_object_or_404(
            UserMessage.objects.filter(
                Q(id=message_id) & Q(user=request.user)
            )
        )
        
        # علامت‌گذاری به عنوان خوانده شده اگر از ادمین است
        if message.is_from_admin and not message.is_read:
            message.mark_as_read()
            logger.info(f"پیام {message_id} توسط کاربر {request.user.username} خوانده شد")
        
        # پیدا کردن مکالمه مرتبط
        conversation_messages = []
        
        if message.contact_message:
            # اگر پیام مربوط به تماس است، تمام پیام‌های این تماس را بیاور
            conversation_messages = UserMessage.objects.filter(
                contact_message=message.contact_message
            ).order_by('created_at')
            
            # پیدا کردن پیام اصلی (اولیه) برای این تماس
            original_message = UserMessage.objects.filter(
                contact_message=message.contact_message,
                is_from_admin=False
            ).first()
        elif message.message_type == 'private':
            # اگر پیام خصوصی است، تمام پیام‌های خصوصی بین این کاربر و ادمین را بیاور
            conversation_messages = UserMessage.objects.filter(
                user=request.user,
                message_type='private'
            ).order_by('created_at')
            original_message = None
        else:
            original_message = None
        
        context = {
            'message': message,
            'conversation_messages': conversation_messages,
            'original_message': original_message,  # اضافه کردن این خط
        }
        return render(request, 'accounts/message_detail.html', context)
        
    except Exception as e:
        logger.error(f"خطا در نمایش جزئیات پیام: {str(e)}")
        messages.error(request, 'پیام مورد نظر یافت نشد.')
        return redirect('my_messages')

@login_required
@user_passes_test(is_admin) 
def send_message_to_user_view(request, user_id=None, message_id=None):
    user = None
    if user_id:
        user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = AdminToUserMessageForm(request.POST)
        if form.is_valid():
            try:
                user_message = form.save(commit=False)
                user_message.user = form.cleaned_data['user']
                user_message.is_from_admin = True
                user_message.sender = request.user
                user_message.is_read = False
                user_message.save()
                
                logger.info(f"پیام مستقیم از ادمین به کاربر {user_message.user.username} ارسال شد")
                messages.success(request, 'پیام با موفقیت ارسال شد!')
                return redirect('dashboard')
            except Exception as e:
                logger.error(f"خطا در ارسال پیام مستقیم: {str(e)}")
                messages.error(request, 'خطا در ارسال پیام. لطفاً مجدداً تلاش کنید.')
    else:
        initial = {}
        if user:
            initial['user'] = user
        if request.original_message:
            initial['subject'] = f"پاسخ به: {request.original_message.subject}"
            initial['content'] = f"\n\n---------- پیام قبلی ----------\n{request.original_message.content}"
        
        form = AdminToUserMessageForm(initial=initial)
    
    users = CustomUser.objects.filter(is_staff=False).order_by('-date_joined')
    pending_messages = ContactMessage.objects.filter(status='pending')
    
    context = {
        'form': form,
        'users': users,
        'selected_user': user,
        'original_message': request.original_message,
    }
    return render(request, 'accounts/send_message_to_user.html', context)

@login_required
@user_passes_test(is_admin)
def admin_view_message_detail(request, message_id, message_type='contact'):
    """نمایش جزئیات پیام برای ادمین"""
    try:
        if message_type == 'contact':
            # نمایش پیام تماس
            message = get_object_or_404(ContactMessage, id=message_id)
            
            # پیدا کردن UserMessage مرتبط
            user_messages = UserMessage.objects.filter(
                contact_message=message
            ).order_by('created_at')
            
            context = {
                'message': message,
                'user_messages': user_messages,
                'message_type': 'contact',
            }
            return render(request, 'accounts/admin_message_detail.html', context)
            
        elif message_type == 'private':
            # نمایش پیام خصوصی
            message = get_object_or_404(UserMessage, id=message_id)
            
            # علامت‌گذاری به عنوان خوانده شده
            if not message.is_read:
                message.mark_as_read()
                logger.info(f"پیام خصوصی {message_id} توسط ادمین خوانده شد")
            
            # پیدا کردن مکالمه
            conversation_messages = UserMessage.objects.filter(
                Q(user=message.user) & Q(message_type='private')
            ).order_by('created_at')
            
            context = {
                'message': message,
                'conversation_messages': conversation_messages,
                'message_type': 'private',
            }
            return render(request, 'accounts/admin_message_detail.html', context)
        
    except Exception as e:
        logger.error(f"خطا در نمایش جزئیات پیام برای ادمین: {str(e)}")
        messages.error(request, 'پیام مورد نظر یافت نشد.')
        return redirect('dashboard')

@login_required
def test_messages_view(request):
    contact_count = ContactMessage.objects.count()
    user_message_count = UserMessage.objects.count()
    unread_count = UserMessage.objects.filter(user=request.user, is_read=False).count()
    recent_messages = UserMessage.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    context = {
        'contact_count': contact_count,
        'user_message_count': user_message_count,
        'unread_count': unread_count,
        'recent_messages': recent_messages,
    }
    return render(request, 'accounts/test_messages.html', context)

@login_required
def test_create_message_view(request):
    if request.method == 'POST':
        message_type = request.POST.get('message_type')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        
        try:
            if message_type == 'contact':
                contact_msg = ContactMessage.objects.create(
                    user=request.user,
                    subject=subject,
                    message=content,
                    status='pending'
                )
                
                UserMessage.objects.create(
                    user=request.user,
                    contact_message=contact_msg,
                    is_from_admin=False,
                    message_type='contact',
                    subject=subject,
                    content=content,
                    sender=request.user,
                    is_read=True
                )
            
            elif message_type == 'response':
                admin_user = CustomUser.objects.filter(is_staff=True).first()
                if admin_user:
                    UserMessage.objects.create(
                        user=request.user,
                        is_from_admin=True,
                        message_type='response',
                        subject=subject,
                        content=content,
                        sender=admin_user,
                        is_read=False
                    )
            
            else:
                admin_user = CustomUser.objects.filter(is_staff=True).first()
                if admin_user:
                    UserMessage.objects.create(
                        user=request.user,
                        is_from_admin=True,
                        message_type='private',
                        subject=subject,
                        content=content,
                        sender=admin_user,
                        is_read=False
                    )
            
            messages.success(request, 'پیام تستی با موفقیت ایجاد شد.')
            
        except Exception as e:
            logger.error(f"خطا در ایجاد پیام تستی: {str(e)}")
            messages.error(request, f'خطا در ایجاد پیام: {str(e)}')
    
    return redirect('test_messages')



@login_required
@user_passes_test(is_admin)
def user_management_view(request):
    """مدیریت کاربران توسط ادمین"""
    # جستجو
    search_query = request.GET.get('search', '')
    user_type_filter = request.GET.get('user_type', '')
    
    # فیلتر کردن کاربران
    users = CustomUser.objects.all().order_by('-date_joined')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(national_code__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    if user_type_filter:
        users = users.filter(user_type=user_type_filter)
    
    # آمار کاربران
    user_stats = {
        'total': CustomUser.objects.count(),
        'normal': CustomUser.objects.filter(user_type='normal').count(),
        'worker': CustomUser.objects.filter(user_type='worker').count(),
        'employee': CustomUser.objects.filter(user_type='employee').count(),
        'staff': CustomUser.objects.filter(is_staff=True).count(),
    }
    
    # صفحه‌بندی
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'user_stats': user_stats,
        'search_query': search_query,
        'user_type_filter': user_type_filter,
        'user_types': CustomUser.USER_TYPE_CHOICES,
    }
    return render(request, 'accounts/user_management.html', context)

@login_required
@user_passes_test(is_admin)
def view_user_detail(request, user_id):
    """نمایش جزئیات کاربر"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # پیام‌های کاربر
    user_messages = UserMessage.objects.filter(user=user).order_by('-created_at')[:10]
    contact_messages = ContactMessage.objects.filter(user=user).order_by('-created_at')[:10]
    
    context = {
        'target_user': user,
        'user_messages': user_messages,
        'contact_messages': contact_messages,
    }
    return render(request, 'accounts/user_detail.html', context)

@login_required
@user_passes_test(is_admin)
def update_user_type(request, user_id):
    """تغییر نوع کاربر"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = UserTypeUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            logger.info(f"نوع کاربر {user.username} توسط ادمین {request.user.username} به {user.user_type} تغییر یافت")
            messages.success(request, f'نوع کاربر {user.get_full_name()} با موفقیت تغییر یافت.')
            return redirect('user_management')
    else:
        form = UserTypeUpdateForm(instance=user)
    
    context = {
        'form': form,
        'target_user': user,
    }
    return render(request, 'accounts/update_user_type.html', context)

@login_required
@user_passes_test(is_admin)
def view_job_document(request, user_id):
    """مشاهده مستند شغلی کاربر"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if not user.job_document:
        messages.error(request, 'این کاربر مستند شغلی آپلود نکرده است.')
        return redirect('user_detail', user_id=user_id)
    
    try:
        # بررسی وجود فایل
        if os.path.exists(user.job_document.path):
            # نمایش فایل در مرورگر
            response = FileResponse(
                open(user.job_document.path, 'rb'),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(user.job_document.name)}"'
            return response
        else:
            messages.error(request, 'فایل مستند شغلی پیدا نشد.')
            return redirect('user_detail', user_id=user_id)
    except Exception as e:
        logger.error(f"خطا در نمایش مستند شغلی: {str(e)}")
        messages.error(request, 'خطا در نمایش مستند شغلی.')
        return redirect('user_detail', user_id=user_id)

@login_required
@user_passes_test(is_admin)
def download_job_document(request, user_id):
    """دانلود مستند شغلی کاربر"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if not user.job_document:
        messages.error(request, 'این کاربر مستند شغلی آپلود نکرده است.')
        return redirect('user_detail', user_id=user_id)
    
    try:
        if os.path.exists(user.job_document.path):
            response = HttpResponse(
                open(user.job_document.path, 'rb').read(),
                content_type='application/octet-stream'
            )
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(user.job_document.name)}"'
            return response
        else:
            messages.error(request, 'فایل مستند شغلی پیدا نشد.')
            return redirect('user_detail', user_id=user_id)
    except Exception as e:
        logger.error(f"خطا در دانلود مستند شغلی: {str(e)}")
        messages.error(request, 'خطا در دانلود مستند شغلی.')
        return redirect('user_detail', user_id=user_id)

@login_required
@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    """فعال/غیرفعال کردن کاربر"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if user == request.user:
        messages.error(request, 'شما نمی‌توانید وضعیت خودتان را تغییر دهید.')
        return redirect('user_management')
    
    user.is_active = not user.is_active
    user.save()
    
    status = "فعال" if user.is_active else "غیرفعال"
    logger.info(f"وضعیت کاربر {user.username} توسط ادمین {request.user.username} به {status} تغییر یافت")
    messages.success(request, f'وضعیت کاربر {user.get_full_name()} به {status} تغییر یافت.')
    
    return redirect('user_management')