from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.core.validators import FileExtensionValidator
from captcha.fields import CaptchaField
from .models import CustomUser, ContactMessage, UserMessage
import jdatetime

class JalaliDateInput(forms.DateInput):
    input_type = 'text'
    
    def __init__(self, attrs=None, format='%Y/%m/%d'):
        if attrs is None:
            attrs = {}
        attrs.update({
            'class': 'form-control jalali-date-input',
            'placeholder': '۱۳۹۹/۰۱/۰۱',
            'autocomplete': 'off'
        })
        super().__init__(attrs, format)

def jalali_to_gregorian(jalali_date_str):
    if not jalali_date_str:
        return None
    try:
        jalali_date = jdatetime.datetime.strptime(jalali_date_str, '%Y/%m/%d')
        gregorian_date = jalali_date.togregorian()
        return gregorian_date
    except:
        return None

class CustomUserCreationForm(UserCreationForm):
    captcha = CaptchaField(label='کد امنیتی')
    birth_date_jalali = forms.CharField(
        label='تاریخ تولد (هجری شمسی)',
        required=False,
        widget=JalaliDateInput(),
        help_text='فرمت: ۱۳۹۹/۰۱/۰۱'
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 
                 'first_name', 'last_name', 'national_code',
                 'profile_image', 'age_group', 'phone_number',
                 'birth_date_jalali', 'address', 'job_document', 'bio', 'website']
        
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'national_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '۱۰ رقم کد ملی'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '۰۹۱۲۳۴۵۶۷۸۹'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'درباره خودتان بنویسید...'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'age_group': forms.Select(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'job_document': forms.FileInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
        
        labels = {
            'profile_image': 'عکس پروفایل',
            'age_group': 'گروه سنی',
            'phone_number': 'شماره موبایل',
            'bio': 'درباره من',
            'website': 'وبسایت',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'user_type' in self.fields:
            del self.fields['user_type']
        
        self.fields['profile_image'].validators = [
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
        ]
        
        if self.instance and self.instance.birth_date:
            jalali_date = jdatetime.date.fromgregorian(date=self.instance.birth_date)
            self.fields['birth_date_jalali'].initial = jalali_date.strftime('%Y/%m/%d')
    
    def clean_birth_date_jalali(self):
        birth_date_jalali = self.cleaned_data.get('birth_date_jalali')
        if birth_date_jalali:
            gregorian_date = jalali_to_gregorian(birth_date_jalali)
            if not gregorian_date:
                raise forms.ValidationError('تاریخ تولد معتبر نیست. فرمت صحیح: ۱۳۹۹/۰۱/۰۱')
            import datetime
            if gregorian_date > datetime.date.today():
                raise forms.ValidationError('تاریخ تولد نمی‌تواند در آینده باشد')
            return gregorian_date
        return None
    
    def save(self, commit=True):
        user = super().save(commit=False)
        birth_date_gregorian = self.cleaned_data.get('birth_date_jalali')
        if birth_date_gregorian:
            user.birth_date = birth_date_gregorian
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    birth_date_jalali = forms.CharField(
        label='تاریخ تولد (هجری شمسی)',
        required=False,
        widget=JalaliDateInput(),
        help_text='فرمت: ۱۳۹۹/۰۱/۰۱'
    )
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'profile_image', 
                 'age_group', 'phone_number', 'birth_date_jalali', 
                 'address', 'job_document', 'bio', 'website']
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'age_group': forms.Select(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'job_document': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
        labels = {
            'profile_image': 'عکس پروفایل',
            'age_group': 'گروه سنی',
            'phone_number': 'شماره موبایل',
            'bio': 'درباره من',
            'website': 'وبسایت',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_image'].validators = [
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
        ]
        
        if self.instance and self.instance.birth_date:
            jalali_date = jdatetime.date.fromgregorian(date=self.instance.birth_date)
            self.fields['birth_date_jalali'].initial = jalali_date.strftime('%Y/%m/%d')
    
    def clean_birth_date_jalali(self):
        birth_date_jalali = self.cleaned_data.get('birth_date_jalali')
        if birth_date_jalali:
            gregorian_date = jalali_to_gregorian(birth_date_jalali)
            if not gregorian_date:
                raise forms.ValidationError('تاریخ تولد معتبر نیست. فرمت صحیح: ۱۳۹۹/۰۱/۰۱')
            import datetime
            if gregorian_date > datetime.date.today():
                raise forms.ValidationError('تاریخ تولد نمی‌تواند در آینده باشد')
            return gregorian_date
        return None
    
    def save(self, commit=True):
        user = super().save(commit=False)
        birth_date_gregorian = self.cleaned_data.get('birth_date_jalali')
        if birth_date_gregorian:
            user.birth_date = birth_date_gregorian
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField(
        label='نام کاربری',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام کاربری'})
    )
    password = forms.CharField(
        label='کلمه عبور',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'رمز عبور'})
    )
    captcha = CaptchaField(label='کد امنیتی')
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('نام کاربری یا کلمه عبور اشتباه است')
        return cleaned_data

class ContactForm(forms.ModelForm):
    captcha = CaptchaField(label='کد امنیتی')
    
    class Meta:
        model = ContactMessage
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

class AdminResponseForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['admin_response']
        widgets = {
            'admin_response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'پاسخ خود را اینجا بنویسید...'
            }),
        }

class UserToAdminMessageForm(forms.ModelForm):
    captcha = CaptchaField(label='کد امنیتی')
    
    class Meta:
        model = UserMessage
        fields = ['subject', 'content']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'موضوع پیام خود را وارد کنید'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'متن پیام خود را اینجا بنویسید...'
            }),
        }
        labels = {
            'subject': 'موضوع پیام',
            'content': 'متن پیام',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        message = super().save(commit=False)
        message.user = self.user
        message.is_from_admin = False
        message.message_type = 'private'
        message.sender = self.user
        message.is_read = True
        if commit:
            message.save()
        return message

class AdminToUserMessageForm(forms.ModelForm):
    class Meta:
        model = UserMessage
        fields = ['user', 'subject', 'content', 'message_type']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'message_type': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = CustomUser.objects.filter(is_staff=False)
        self.fields['user'].label = 'کاربر گیرنده'
        self.fields['subject'].label = 'موضوع پیام'
        self.fields['content'].label = 'متن پیام'
        self.fields['message_type'].label = 'نوع پیام'


class UserTypeUpdateForm(forms.ModelForm):
    """فرم تغییر نوع کاربر توسط ادمین"""
    class Meta:
        model = CustomUser
        fields = ['user_type']
        widgets = {
            'user_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
        }
        labels = {
            'user_type': 'نوع کاربر',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_type'].choices = CustomUser.USER_TYPE_CHOICES