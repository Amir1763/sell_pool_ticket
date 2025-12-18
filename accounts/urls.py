from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),


    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('contact/', views.contact_view, name='contact'),
    path('about/', views.about_view, name='about'),
    
       # پیام‌رسانی کاربر
    path('messages/', views.my_messages_view, name='my_messages'),
    path('messages/<int:message_id>/', views.view_my_message_detail, name='view_my_message_detail'),
    path('send-private-message/', views.send_private_message_view, name='send_private_message'),
    
    # URLهای ادمین برای پیام‌رسانی
    path('send-message/', views.send_message_to_user_view, name='send_message'),
    path('send-message/<int:user_id>/', views.send_message_to_user_view, name='send_message_to_user'),
    path('send-message/<int:user_id>/<int:message_id>/', views.send_message_to_user_view, name='reply_to_message'),
    path('respond/<int:message_id>/', views.respond_message_view, name='respond_message'),

        # مدیریت کاربران توسط ادمین
    path('admin/users/', views.user_management_view, name='user_management'),
    path('admin/users/<int:user_id>/', views.view_user_detail, name='user_detail'),
    path('admin/users/<int:user_id>/update-type/', views.update_user_type, name='update_user_type'),
    path('admin/users/<int:user_id>/view-document/', views.view_job_document, name='view_job_document'),
    path('admin/users/<int:user_id>/download-document/', views.download_job_document, name='download_job_document'),
    path('admin/users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
]