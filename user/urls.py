from django.urls import path
from . import views

app_name = 'user'
urlpatterns = [
    # fb function base
    # path('login/', views.user_login, name='login'),
    # path('register/', views.user_register, name='register'),
    # path('logout/', views.user_logout, name='logout'),
    # path('dashboard/<int:user_id>/', views.user_dashboard, name='dashboard'),

    # cv
    path('login/', views.UserLogin.as_view(), name="login"),
    path('register/', views.SignUpView.as_view(), name="register"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    # path('profile/', views.CreateProfile.as_view(), name="profile_create"),
    # path('dashboard/<int:user_id>/', views.UserDashboard.as_view(), name='dashboard'),
    # path('dashboard/<int:user_id>/', views.UserDashboard2.as_view(), name='dashboard'),
    path('dashboard/<int:user_id>/', views.UserDashboardPost.as_view(), name='dashboard'),
    path('edit_profile/<int:user_id>/', views.ProfileEditView.as_view(), name='edit_profile'),
    # path('edit_profile/<int:user_id>/', views.ProfileEditGenericView.as_view(), name='edit_profile'),
    # path("edit_profile/<int:pk>/", views.EditProfile2.as_view(), name="edit_profile"),

    # sms
    # path('phone_login/', views.phone_login, name='phone_login'),
    path('phone_login/', views.PhoneLogin.as_view(), name='phone_login'),
    # path('verify/', views.verify, name='verify'),
    path('verify/', views.Verify.as_view(), name='verify'),

    # follow & unfollow
    # path('follow/', views.follow, name='follow'),
    path('follow/', views.Follow.as_view(), name='follow'),
    # path('unfollow/', views.unfollow, name='unfollow'),
    path('follow/', views.UnFollow.as_view(), name='unfollow'),

]
