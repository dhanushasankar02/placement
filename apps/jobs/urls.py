from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('<int:pk>/', views.job_detail, name='job_detail'),
    path('create/', views.job_create, name='job_create'),
    path('<int:pk>/update/', views.job_update, name='job_update'),
    path('<int:pk>/delete/', views.job_delete, name='job_delete'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('search/', views.search_jobs, name='search_jobs'),
    path('categories/', views.job_categories, name='job_categories'),
    path('<int:pk>/save/', views.save_job_view, name='save_job'),
    path('saved/', views.saved_jobs, name='saved_jobs'),
]
