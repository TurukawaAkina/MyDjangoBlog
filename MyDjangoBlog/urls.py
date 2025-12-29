from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # 标准 allauth 路由
    path('accounts/', include('allauth.urls')),

    # 别名路由，直接通过 name 绑定，不建议在这里写复杂的 lambda
    path('login/', lambda r: redirect('account_login'), name='login'),
    path('register/', lambda r: redirect('account_signup'), name='register'),
    path('logout/', lambda r: redirect('account_logout'), name='logout'),

    path('', include('blog.urls')),
    path('profile/', user_views.profile_view, name='profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)