from django.urls import path
from . import views

app_name = 'interviews'

urlpatterns = [
    path('', views.interview_list, name='interview_list'),
    path('schedule/', views.interview_schedule, name='interview_schedule'),
    path('schedule/<int:app_id>/', views.interview_schedule, name='interview_schedule_app'),
    path('<int:pk>/', views.interview_detail, name='interview_detail'),
    path('<int:pk>/result/', views.interview_result, name='interview_result'),
    path('<int:pk>/feedback/', views.interview_feedback, name='interview_feedback'),
    path('calendar/', views.interview_calendar, name='interview_calendar'),
]
