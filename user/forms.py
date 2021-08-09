from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models import fields
from django.http.request import validate_host
from .models import Profile


# Form
# class UserLoginForm(forms.Form):
# 	username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Username'}))
# 	password = forms.CharField(max_length=40, widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Password'}))

# messages = {
# 	'required':'این فیلد اجباری است',
# 	'invalid':'لطفا یک ایمیل معتبر وارد کنید',
# 	'max_length':'تعداد کاراکترها بیشتر از حد مجاز است'}

# class UserRegistrationForm(forms.Form):
# 	username = forms.CharField(error_messages=messages, max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
# 	email = forms.EmailField(error_messages=messages, max_length=50, widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Email'}))
# 	password1 = forms.CharField(error_messages=messages, max_length=40, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
# 	password2 = forms.CharField(error_messages=messages, max_length=40, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

# 	def clean_pass(self):
# 		pass1 = self.cleaned_data.get('password1')
# 		pass2 = self.cleaned_data.get('password2')
# 		self.initial
# 		if pass1 == pass2:
# 			return True
# 		return False

# 	def save(self, *args, **kwargs):
# 		if self.clean_pass():
# 			user = User.objects.create_user(
# 				username=self.cleaned_data['username'],
# 				email=self.cleaned_data['email'],
# 				password=self.cleaned_data['password1']
# 			)
# 			return user
# 		return None


# ModelForm
# Login
class UserLoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')

# Registration
class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'username', 'password1', 'password2')
        error_messages = {
            'username': {
                'required': 'این فیلد اجباری است',
                'invalid': 'لطفا یک نام کاربری معتبر وارد کنید',
                # 'invalid_email': 'Email is invalid.',
                'max_length': 'تعداد کاراکترها بیشتر از حد مجاز است',

            },
            'email': {
                'required': 'این فیلد اجباری است',
                'invalid': 'لطفا یک ایمیل معتبر وارد کنید',
                'max_length': 'تعداد کاراکترها بیشتر از حد مجاز است',

            },
            'password': {
                'required': 'این فیلد اجباری است',
                'invalid': 'لطفا یک پسورد معتبر وارد کنید',
                'max_length': 'تعداد کاراکترها بیشتر از حد مجاز است',

            },
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')

        if p1 and p2:
            if p1 != p2:
                raise forms.ValidationError('passwords must match')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data["email"]
        user = User.objects.filter(email=email)
        if user.exists():
            raise forms.ValidationError('This email already exists')
        return email


# UserCreationForm
# https://studygyaan.com/django/how-to-create-sign-up-registration-view-in-django
# class UserRegistrationForm(UserCreationForm):
# 	first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
# 	last_name = forms.CharField(max_length=30, required=False, help_text='Optional')
# 	email = forms.EmailField(max_length=254, help_text='Enter a valid email address')

# profile
class ProfileCreationForm(forms.ModelForm):
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = Profile
        fields = ('age', 'phone', 'username', 'password1', 'password2', 'first_name', 'last_name', 'email')


# edit profile
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'age', 'phone')



# login with code number(sms)
class PhoneLoginForm(forms.Form):
    phone = forms.IntegerField()

    def clean_phone(self):
        phone = Profile.objects.filter(phone=self.cleaned_data['phone'])
        if not phone.exists():
            raise forms.ValidationError('This phone number does not exists')
        return self.cleaned_data['phone']


class VerifyCodeForm(forms.Form):
    code = forms.IntegerField()

