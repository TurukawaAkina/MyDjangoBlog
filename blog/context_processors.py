# blog/context_processors.py
from .models import Post, Category

def blog_sidebar_data(request):
    """
    全站通用的侧边栏数据：热门推荐和分类列表
    """
    return {
        # 热门文章
        'hot_posts': Post.objects.all().order_by('-views')[:5],
        # 所有分类（用于侧边栏或导航栏）
        'categories': Category.objects.all(),
    }