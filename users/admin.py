from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserTitle


# 注册用户模型
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 在后台列表页显示的字段
    list_display = ('username', 'email', 'nickname', 'level', 'experience', 'is_staff')

    # 在编辑页分类显示的字段
    fieldsets = UserAdmin.fieldsets + (
        ('成长系统', {'fields': ('nickname', 'avatar', 'bio', 'level', 'experience', 'custom_title')}),
    )
    # 在创建页显示的字段
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('成长系统', {'fields': ('nickname', 'avatar', 'bio', 'level', 'experience', 'custom_title')}),
    )


# 注册头衔模型
@admin.register(UserTitle)
class UserTitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'icon_class')