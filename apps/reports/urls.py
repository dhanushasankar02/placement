from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('placement/', views.placement_report, name='placement_report'),
    path('student/', views.student_report, name='student_report'),
    path('company/', views.company_report, name='company_report'),
    path('job/', views.job_report, name='job_report'),
    path('interview/', views.interview_report, name='interview_report'),
    path('analytics/', views.analytics_view, name='analytics'),
]
