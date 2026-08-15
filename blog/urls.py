from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('categoria/<slug:category_slug>/', views.PostListView.as_view(), name='post_list_by_category'),
    path('tag/<slug:tag_slug>/', views.PostListView.as_view(), name='post_list_by_tag'),
    path('<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
]