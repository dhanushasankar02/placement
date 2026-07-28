from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('', views.application_list, name='application_list'),
    path('<int:pk>/', views.application_detail, name='application_detail'),
    path('apply/<int:job_id>/', views.application_create, name='application_create'),
    path('<int:pk>/status-update/', views.application_status, name='application_status'),
    path('history/', views.application_history, name='application_history'),
    path('shortlisted/', views.shortlisted_view, name='shortlisted'),
    path('rejected/', views.rejected_view, name='rejected'),
    path('selected/', views.selected_view, name='selected'),
]
