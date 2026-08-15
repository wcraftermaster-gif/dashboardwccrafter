from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),
    path('posts/', views.DashboardPostListView.as_view(), name='post_list'),
    path('posts/nuevo/', views.DashboardPostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/editar/', views.DashboardPostUpdateView.as_view(), name='post_edit'),
    path('posts/<int:pk>/eliminar/', views.DashboardPostDeleteView.as_view(), name='post_delete'),
]