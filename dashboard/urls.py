from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),

    path('posts/', views.DashboardPostListView.as_view(), name='post_list'),
    path('posts/nuevo/', views.DashboardPostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/editar/', views.DashboardPostUpdateView.as_view(), name='post_edit'),
    path('posts/<int:pk>/eliminar/', views.DashboardPostDeleteView.as_view(), name='post_delete'),

    path('categorias/', views.category_list, name='category_list'),
    path('categorias/<slug:slug>/editar/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categorias/<slug:slug>/eliminar/', views.CategoryDeleteView.as_view(), name='category_delete'),

    path('etiquetas/', views.tag_list, name='tag_list'),
    path('etiquetas/<slug:slug>/editar/', views.TagUpdateView.as_view(), name='tag_edit'),
    path('etiquetas/<slug:slug>/eliminar/', views.TagDeleteView.as_view(), name='tag_delete'),

    path('usuarios/', views.UserListView.as_view(), name='user_list'),
    path('usuarios/nuevo/', views.UserCreateView.as_view(), name='user_create'),
    path('usuarios/<int:pk>/editar/', views.UserUpdateView.as_view(), name='user_edit'),
    path('usuarios/<int:pk>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),

    path('perfil/', views.ProfileUpdateView.as_view(), name='profile'),
]