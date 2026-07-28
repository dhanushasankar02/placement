from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/password/', views.change_password_view, name='change_password'),
    path('password-reset/', views.forgot_password_view, name='forgot_password'),
    path('password-reset/confirm/', views.reset_password_view, name='reset_password'),
    path('verify-email/', views.verify_email_view, name='verify_email'),
]
