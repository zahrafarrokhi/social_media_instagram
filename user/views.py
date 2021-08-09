from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from posts.models import Post
from .models import Profile,Relation
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, UserLoginForm, EditProfileForm, PhoneLoginForm, VerifyCodeForm, \
    ProfileCreationForm
# cbv
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
# logout
from django.views.generic import View  # logout #2
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
# sms
from random import randint
from kavenegar import *
# verify
from django.contrib.auth import login
# follow & unfollow
from django.http import JsonResponse


class UserLogin(LoginView):
    template_name = 'user/login.html'
    from_class = UserLoginForm

    def get_success_url(self):
        messages.success(self.request, 'you logged in successfully', 'success')
        return reverse_lazy('posts:all_posts')


class SignUpView(CreateView):
    template_name = 'user/register.html'
    form_class = UserRegistrationForm
    # success_url = reverse_lazy('user:login')

    def get_success_url(self):
        messages.success(self.request, 'you signup in successfully', 'success')
        return reverse_lazy('user:login')

    # make profile for user or use signal
    # def form_valid(self, form):
    #     user = form.save(commit=False)
    #     user.is_active = False
    #     user.save()
    #     # make profile for user or use signal
    #     Profile.objects.create(user=user)
    #     login(self.request, user)
    #     return super().form_valid(form)


# logout(LoginRequiredMixin, LogoutView) or (LoginRequiredMixin,View)
# 1
class LogoutView(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy('posts:all_posts')
    login_url = reverse_lazy('user:login')


# 2
# class LogoutView(LoginRequiredMixin,View):
#     login_url = reverse_lazy('user:login')

#     def get(self, request):
#         logout(request)
#         messages.success(self.request, 'you logged out successfully', 'success')
#         return redirect('posts:all_posts')


# profile
# class CreateProfile(CreateView):
#     template_name = 'user/profile-create.html'
#     form_class = ProfileCreationForm


# UserDashboard with View & DetailView
# class UserDashboard(View):
#     def get(self, request,user_id):
#         user = get_object_or_404(User, pk=user_id)
#         return render(request, 'user/dashboard.html', {'user':user})

# class UserDashboard2(DetailView):
#     template_name = 'user/dashboard.html'
#     model = User
#     context_object_name = 'post'
#     pk_url_kwarg = 'user_id'

# Show User posts in Dashboard
class UserDashboardPost(LoginRequiredMixin, View):
    login_url = reverse_lazy('user:login')

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        posts = Post.objects.filter(user=user)
        # dash => A user who logs in if the dashboard itself shows the AddPost class(if in dashbord-post.html)
        self_dash = False
        if request.user.id == user_id:
            self_dash = True
        # is_following = False
        # relation = Relation.objects.filter(from_user=request.user, to_user=user)
        # if relation.exists():
        #     is_following = True

        return render(request, 'user/dashboard-post.html', {'user': user, 'posts': posts,'self_dash':self_dash})

# addpost view in app post

# edit profile(ok)
class ProfileEditView(LoginRequiredMixin, View):

    def get_object(self, *args, **kwargs):
        user = get_object_or_404(User, pk=self.kwargs['user_id'])
        return user.profile

    def get(self, request, user_id):
        form = EditProfileForm(instance=self.get_object(user_id))
        return render(request, "user/edit_profile.html", {"form": form})

    def post(self, request, user_id):
        form = EditProfileForm(request.POST, instance=self.get_object(user_id))
        if form.is_valid():
            form.save()
            # form.instance.email = form.cleaned_data['email']
            # form.instance.save()
            messages.success(request, 'your profile edited successfully', 'success')
            return redirect(reverse_lazy('user:dashboard', kwargs={'user_id':self.request.user.pk}))
        return render(request, "user/edit_profile.html", {"form": form})

# UpdateView(ok)
class ProfileEditGenericView(UpdateView):
    form_class = EditProfileForm
    model = Profile
    context_object_name = 'form'
    template_name = 'user\edit_profile.html'

    def get_object(self, *args, **kwargs):
        user = get_object_or_404(User, pk=self.kwargs['user_id'])
        return user.profile

    def get_success_url(self):
        url = reverse_lazy('user:dashboard', args=[self.request.user.pk])
        return url

# sms(ok)
class PhoneLogin(View):

    def get(self, request):
        form = PhoneLoginForm()
        return render(request, 'user/phone_login.html', {'form': form})

    def post(self, request):
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            global phone, rand_num
            phone = f"0{form.cleaned_data['phone']}"
            rand_num = randint(1000, 9999)
            api = KavenegarAPI(
                '6F4C7A3478307A66764E51314D383855414156377A7A6177444C54755A787268424C715355684C7A7535493D')
            params = {'sender': '', 'receptor': phone, 'message': rand_num}
            api.sms_send(params)
            # messages.success(request, 'your send successfully', 'success')
            return redirect('user:verify')
        return render(request, 'user/phone_login.html', {'form': form})


class Verify(View):
    def get(self, request):
        form = VerifyCodeForm()
        return render(request, 'user/verify.html', {'form': form})

    def post(self, request):
        form = VerifyCodeForm(request.POST)
        if form.is_valid():
            if rand_num == form.cleaned_data['code']:
                profile = get_object_or_404(Profile, phone=phone)
                user = get_object_or_404(User, profile__id=profile.id)
                login(request, user)
                messages.success(request, 'logged in successfully', 'success')
                return redirect('posts:all_posts')
            else:
                messages.error(request, 'your code is wrong', 'warning')
        return render(request, 'user/verify.html', {'form': form})
# test
# kavenegar.com
# pip install kavenegar
# logged in successfully

# follow & unfollow(ok)
class Follow(LoginRequiredMixin, View):
    def post(self, request):
        user_id = self.request.POST['user_id']
        following = get_object_or_404(User, pk=user_id)
        check_relation = Relation.objects.filter(from_user=request.user, to_user=following)
        if check_relation.exists():
            return JsonResponse({'status': 'exists'})
        else:
            Relation(from_user=request.user, to_user=following).save()
            return JsonResponse({'status': 'ok'})

# ok
class UnFollow(LoginRequiredMixin, View):
    def post(self, request):
        user_id = self.request.POST['user_id']
        following = get_object_or_404(User, pk=user_id)
        check_relation = Relation.objects.filter(from_user=request.user, to_user=following)
        if check_relation.exists():
            check_relation.delete()
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'notexists'})
