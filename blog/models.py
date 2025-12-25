from django.db import models
from django.conf import settings
import markdown
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="分类名称")
    def __str__(self): return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name="标签名称")
    def __str__(self): return self.name

class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="作者")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="分类")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="标签")
    views = models.PositiveIntegerField(default=0, verbose_name="阅读量")
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='blog_posts', blank=True, verbose_name="点赞")
    banner = models.ImageField(upload_to='blog/banners/', blank=True, null=True, verbose_name="封面图")

    def __str__(self): return self.title
    def total_likes(self): return self.likes.count()
    def get_content_html(self):
        return markdown.markdown(self.content, extensions=['extra', 'codehilite', 'toc'])

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: {self.content[:20]}'

@receiver(post_save, sender=Post)
def increase_xp_on_post(sender, instance, created, **kwargs):
    if created:
        instance.author.add_experience(50)

@receiver(post_save, sender=Comment)
def increase_xp_on_comment(sender, instance, created, **kwargs):
    if created:
        instance.user.add_experience(10)