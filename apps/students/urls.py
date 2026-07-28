from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('create/', views.student_create, name='student_create'),
    path('<int:pk>/update/', views.student_update, name='student_update'),
    path('<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('resume-upload/', views.resume_upload, name='resume_upload'),
    path('skills/', views.skills_view, name='skills'),
    path('education/', views.education_view, name='education'),
    path('certificates/', views.certificates_view, name='certificates'),
    path('applied/', views.applied_jobs, name='applied_jobs'),
    path('shortlisted/', views.shortlisted_jobs, name='shortlisted_jobs'),
    path('interviews/', views.interview_schedule, name='interview_schedule'),
    path('status/', views.placement_status, name='placement_status'),
]
