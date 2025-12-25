from django.contrib import admin
from .models import Category, Tag, Post, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'views') # 后台列表显示的列
    search_fields = ('title', 'content') # 支持搜索的字段
    list_filter = ('category', 'created_at') # 右侧筛选栏

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Comment)