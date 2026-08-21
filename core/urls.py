from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('cron/publish-scheduled/<str:token>/', views.cron_publish_scheduled, name='cron_publish_scheduled'),
]