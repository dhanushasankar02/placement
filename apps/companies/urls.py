from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('', views.company_list, name='company_list'),
    path('<int:pk>/', views.company_detail, name='company_detail'),
    path('create/', views.company_create, name='company_create'),
    path('<int:pk>/update/', views.company_update, name='company_update'),
    path('<int:pk>/delete/', views.company_delete, name='company_delete'),
    path('my-profile/', views.company_profile, name='company_profile'),
    path('my-jobs/', views.company_jobs, name='company_jobs'),
    path('my-candidates/', views.company_students, name='company_students'),
]
