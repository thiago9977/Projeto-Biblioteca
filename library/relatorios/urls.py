from django.urls import path

from . import views

app_name = 'relatorios'

urlpatterns = [
    path('', views.dashboard_relatorios, name='admin_reports'),
]
