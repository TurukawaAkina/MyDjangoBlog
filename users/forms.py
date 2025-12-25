from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='邮箱')

    class Meta:
        model = User
        fields = ['username', 'email', 'nickname']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nickname', 'avatar', 'bio']
        labels = {
            'nickname': '昵称',
            'avatar': '头像',
            'bio': '个人简介',
        }
        widgets = {
            'nickname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '请输入昵称'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '介绍一下你自己吧...'
            }),
        }