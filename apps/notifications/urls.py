from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('<int:pk>/', views.notification_detail, name='notification_detail'),
    path('unread/', views.unread_notifications, name='unread_notifications'),
    path('email-templates/', views.email_templates, name='email_templates'),
    path('webmail/', views.webmail, name='webmail'),
]
