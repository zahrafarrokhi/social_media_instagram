from django.shortcuts import render,get_object_or_404,redirect
from django.http import request
from django.utils.functional import lazy
from .forms import AddPostForm, EditPostForm,AddCommentForm,AddReplyForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.text import slugify
from .models import Post,Comment,Vote
#redis
import redis
from django.conf import settings
# baseview
from django.views import View
# generic
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView,FormView
# mixin
from django.views.generic.edit import FormMixin
# LoginRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin

redis_con = redis.Redis(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)

# Create your views here.
class AllPosts(ListView):
    template_name = 'posts/all_posts.html'
    model = Post
    context_object_name = 'posts' # object_list
    ordering = ['-created']


class PostDetail(FormMixin,DetailView):
    template_name = 'posts/post_detail.html'
    model = Post
    context_object_name = 'post'  # object_list
    slug_field = 'slug' # model field
    slug_url_kwarg = 'slug' # slug name in your url
    form_class = AddCommentForm
    second_form_class = AddReplyForm



    # def get_queryset(self,**kwargs) :
    #     return Post.objects.filter(slug=self.kwargs['slug'])

    def get_success_url(self):
        return reverse_lazy('posts:post_detail', kwargs={'slug': self.kwargs['slug']})


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        slug = self.kwargs['slug']
        # slug = self.kwargs[self.slug_url_kwarg]
        post = get_object_or_404(Post,slug=slug)
        comments = Comment.objects.filter(post=post, is_reply=False)
        context['comments'] = comments
        redis_con.hsetnx('post_views', post.id, 0)
        rviews = redis_con.hincrby('post_views', post.id)
        context['rviews'] = rviews
        context['form'] = AddCommentForm()
        context['reply'] = AddReplyForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        slug = self.kwargs['slug']
        post = get_object_or_404(Post, slug=slug)
        form = form.save(commit=False)
        form.post = post
        form.user = self.request.user
        form.save()
        messages.success(self.request, 'you comment submitted successfully')
        return super().form_valid(form)


    # َAddPost

# AddPost (FormView,CreateView) Ok
class AddPost(LoginRequiredMixin, FormView):
    template_name = 'posts/add_post.html'
    form_class = AddPostForm

    # success_url = reverse_lazy('user:dashboard')

    def get_success_url(self, **kwargs):
        return reverse_lazy('user:dashboard', kwargs={'user_id': self.request.user.id})

    # if request.user.id == user_id:
    def form_valid(self, form):
        if self.request.user.id == self.kwargs['user_id']:
            self.add_post(form.cleaned_data)
            return super().form_valid(form)

    def add_post(self, data):
        new_post = Post(user=self.request.user, body=data['body'], slug=slugify(data['body'][:30]))
        new_post.save()
        messages.success(self.request, 'your post submitted', 'success')

# CreateView(ok)
class AddPostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['body']
    template_name = 'posts/add_post.html'

    # form_class = AddPostForm
    # success_url = reverse_lazy('user:dashboard')

    def get_success_url(self, **kwargs):
        return reverse_lazy('user:dashboard', kwargs={'user_id': self.request.user.id})

    # if request.user.id == user_id:
    def form_valid(self, form):
        if self.request.user.id == self.kwargs['user_id']:
            new_post = form.save(commit=False)
            new_post.user = self.request.user
            new_post.slug = slugify(form.cleaned_data['body'][:30])
            new_post.save()
            messages.success(self.request, 'your post submitted', 'success')
            return super().form_valid(form)

#PostDelete (ok)
class PostDeleteView(LoginRequiredMixin,View):

    def post(self,request, user_id, post_id):
        if self.request.user.id == self.kwargs['user_id']:
            # Post.objects.filter(pk=post_id).delete()
            p = Post.objects.filter(pk=post_id)
            p.delete()
            messages.success(request, 'your post deleted successfully', 'success')
            return redirect('user:dashboard', user_id)

# DeleteView(ok)
class PostDeleteGenericView(LoginRequiredMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    # success_url ="/"

    def get_success_url(self, **kwargs):
        return reverse_lazy('user:dashboard', kwargs={'user_id': self.request.user.id})

    def post(self, request, user_id, post_id):
        if self.request.user.id == self.kwargs['user_id']:
            messages.success(request, 'your post deleted successfully', 'success')
            return super().post(request)
        else:
            # return "you dont delete this post"
            messages.error(request, 'your dont  deleted this post', 'error')
            return redirect('user:dashboard', user_id)

# edit(ok)
class PostEditView(LoginRequiredMixin,View):
    # if self.request.user.id == self.user_id:
    def get_object(self,post_id):
        post = get_object_or_404(Post, pk=post_id)
        return post

    def get(self, request,user_id, post_id):
        if self.request.user.id == self.kwargs['user_id']:
            form = EditPostForm(instance=self.get_object(post_id))
            return render(request, "posts/edit_post.html", {"form": form})
        else:
            return redirect('posts:all_posts')

    def post(self,request,user_id, post_id):
        if self.request.user.id == self.kwargs['user_id']:
            form = EditPostForm(request.POST, instance=self.get_object(post_id))
            if form.is_valid():
                ep = form.save(commit=False)
				# change body =>change slug
                ep.slug = slugify(form.cleaned_data['body'][:30])
                ep.save()
                messages.success(request, 'your post edited successfully', 'success')
                return redirect('user:dashboard', user_id)
            return render(request, "posts/edit_post.html", {"form": form})
        else:
            return redirect('posts:all_posts')

# UpdateView(ok)
class PostEditGenericView(LoginRequiredMixin,UpdateView):
    form_class = EditPostForm
    template_name = "posts/edit_post.html"
    model = Post

    def get_success_url(self,**kwargs):
        return reverse_lazy('user:dashboard',kwargs = { 'user_id': self.request.user.id})

    def get_context_data(self, **kwargs):
        form = EditPostForm(instance=self.get_object())
        context = {'form': form}
        return context

# reply(ok)
class AddReply(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = 'posts/post_detail.html'
    form_class = AddReplyForm
    # success_url = reverse_lazy('user:dashboard ')

    def form_valid(self, form):
        form.instance =form.save(commit=False)
        form.instance.user = self.request.user
        # post = Post.objects.get(id=self.kwargs['post_id'])
        post = get_object_or_404(Post,id=self.kwargs['post_id'])
        form.instance.post = post
        # comment = Comment.objects.get(pk=self.kwargs['comment_id'])
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        form.instance.reply = comment
        form.instance.is_reply=True
        form.instance.save()
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        messages.success(self.request, 'your reply for this comment  submitted', 'success')
        post = Post.objects.get(pcomment=self.kwargs['comment_id'])
        return post.get_absolute_url()

# like(Ok)
class PostLike(LoginRequiredMixin,View):
    def get(self,request,post_id):
        post = get_object_or_404(Post, id=post_id)
        like = Vote(post=post, user=request.user)
        like.save()
        messages.success(request, 'you liked successfully', 'success')
        return redirect('posts:post_detail', post.slug)

