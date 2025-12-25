"""
URL configuration for MyDjangoBlog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # 博客应用路由 (已包含 blog 命名空间)
    path('', include('blog.urls')),

    # 用户相关
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile_view, name='profile'),

    # 登录配置：登录成功后跳转到 blog:post_list
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html',
        next_page='blog:post_list'
    ), name='login'),

    # 注销配置：注销后跳转到 blog:post_list
    # 注意：Django 5.0+ 默认只接受 POST 请求注销
    path('logout/', auth_views.LogoutView.as_view(
        next_page='blog:post_list'
    ), name='logout'),
]

# 开发环境下服务媒体文件（如头像、封面图）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)