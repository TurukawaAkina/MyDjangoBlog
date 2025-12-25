from django.urls import path
from . import views

# 必须添加这一行，否则模板中的 {% url 'blog:post_detail' ... %} 会报错
app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('post-like/<int:pk>/', views.post_like, name='post_like'),
]