from django.urls import path
from . import views

app_name = 'posts'
urlpatterns = [
    # all-detail-add-delete-edit
    # fb
    # path('', views.all_posts, name='all_posts'),
    # path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.post_detail, name='post_detail'),
    # path('add_post/<int:user_id>/', views.add_post, name='add_post'),
    # path('post_delete/<int:user_id>/<int:post_id>/', views.post_delete, name='post_delete'),
    # path('post_edit/<int:user_id>/<int:post_id>/', views.post_edit, name='post_edit'),
    # reply
    # path('add_reply/<int:post_id>/<int:comment_id>/', views.add_reply, name='add_reply'),
    # like
    # path('like/<int:post_id>/', views.post_like, name='post_like'),

    # cb
    path('', views.AllPosts.as_view(), name='all_posts'),
    # path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('<str:slug>/', views.PostDetail.as_view(), name='post_detail'),
    path('add_post/<int:user_id>/', views.AddPost.as_view(), name='add_post'),
    path('post_delete/<int:user_id>/<int:post_id>/', views.PostDeleteView.as_view(), name='post_delete'),
    # path('post_delete/<int:user_id>/<int:pk>/', views.PostDeleteGenericView.as_view(), name='post_delete'),
    # path('post_edit/<int:user_id>/<int:post_id>/', views.PostEditView.as_view(), name='post_edit'),
    path('post_edit/<int:user_id>/<int:pk>/', views.PostEditGenericView.as_view(), name='post_edit'),

    # reply
    path('add_reply/<int:post_id>/<int:comment_id>/', views.AddReply.as_view(), name='add_reply'),
    # like
    path('like/<int:post_id>/', views.PostLike.as_view(), name='post_like'),

]
