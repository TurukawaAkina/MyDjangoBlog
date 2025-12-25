from django.urls import path
from .views import register, profile_view

app_name = 'users'

urlpatterns = [
    path('register/', register, name='register'),
    path('profile/', profile_view, name='profile'),
]