"""
Django settings for MyDjangoBlog project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-(=u&e=iyp9x=fdv$w7xg5mzv+5_dc%(bv4f%_^n*%ww4vv!&+l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 第三方库
    'crispy_forms',
    'crispy_bootstrap5',
    'django.contrib.sites',

    # Allauth 认证体系
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',

    # 本地 App
    'users.apps.UsersConfig',
    'blog.apps.BlogConfig',
]

SITE_ID = 1

# 认证后端设置
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# --- Allauth 核心设置 ---
LOGIN_URL = '/login/'                # 统一登录入口别名
LOGIN_REDIRECT_URL = '/'             # 登录后跳转首页
LOGOUT_REDIRECT_URL = '/login/'      # 注销后直接跳转回登录页（强制登录逻辑）
ACCOUNT_LOGOUT_REDIRECT_URL = '/login/'
ACCOUNT_EMAIL_VERIFICATION = "none"  # 开发环境不验证邮箱
ACCOUNT_LOGOUT_ON_GET = True         # 点击注销直接退出
SOCIALACCOUNT_LOGIN_ON_GET = True    # 社交登录跳过中间页
SOCIALACCOUNT_AUTO_SIGNUP = True     # 自动注册

# 第三方登录配置
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'}
    },
    'github': {
        'SCOPE': ['user', 'repo'],
    }
}

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# 使用自定义用户模型
AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 你的自定义中间件
    'users.middleware.DailyLoginXPMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'MyDjangoBlog.middleware.LoginRequiredMiddleware',
]

ROOT_URLCONF = 'MyDjangoBlog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 修正：这里必须准确指向 templates 文件夹
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blog.context_processors.blog_sidebar_data',
            ],
        },
    },
]

WSGI_APPLICATION = 'MyDjangoBlog.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'my_blog_db',
        'USER': 'root',
        'PASSWORD': 'TaNuKi_070502',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static and Media files
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'