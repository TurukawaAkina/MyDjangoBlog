from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Tag, Comment
from .forms import CommentForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


# --- 1. 文章列表（包含分页、搜索、分类过滤） ---
def post_list(request):
    # 获取筛选参数
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')

    # 获取基础查询集
    posts_list = Post.objects.all().order_by('-created_at')

    # 搜索逻辑
    if search_query:
        posts_list = posts_list.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # 分类过滤逻辑
    current_category = None
    if category_id:
        current_category = get_object_or_404(Category, id=category_id)
        posts_list = posts_list.filter(category_id=category_id)

    # --- 分页核心代码 ---
    # 每页显示 5 篇文章
    paginator = Paginator(posts_list, 6)
    page_number = request.GET.get('page')

    try:
        posts = paginator.get_page(page_number)
    except PageNotAnInteger:
        # 如果页码不是整数，返回第一页
        posts = paginator.page(1)
    except EmptyPage:
        # 如果页码超出范围，返回最后一页
        posts = paginator.page(paginator.num_pages)

    # 返回上下文
    return render(request, 'blog/post_list.html', {
        'posts': posts,  # 模板中循环这个变量
        'search_query': search_query,
        'current_category': current_category,
    })


# --- 2. 文章详情 ---
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # 阅读量增加
    post.views += 1
    post.save(update_fields=['views'])

    # 获取顶级评论（非回复）
    comments = post.comments.filter(parent=None).order_by('-created_at')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('account_login')  # 这里的URL名称需根据你的urls.py调整

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user

            # 处理回复功能
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent_id = parent_id

            comment.save()

            # 增加用户经验
            if hasattr(request.user, 'experience'):
                request.user.experience += 5
                request.user.save()

            return redirect('blog:post_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': form
    })


# --- 3. 写文章 ---
@login_required
def post_create(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        banner = request.FILES.get('banner')

        if title and content and category_id:
            post = Post.objects.create(
                title=title,
                content=content,
                author=request.user,
                category_id=category_id,
                banner=banner
            )

            # 奖励经验值
            if hasattr(request.user, 'experience'):
                request.user.experience += 20
                request.user.save()

            return redirect('blog:post_detail', pk=post.pk)

    categories = Category.objects.all()
    return render(request, 'blog/post_form.html', {'categories': categories})


# --- 4. 编辑文章 ---
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # 权限检查：只有作者本人能编辑
    if post.author != request.user:
        return redirect('blog:post_list')

    if request.method == "POST":
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.category_id = request.POST.get('category')

        if request.FILES.get('banner'):
            post.banner = request.FILES.get('banner')

        post.save()
        return redirect('blog:post_detail', pk=post.pk)

    categories = Category.objects.all()
    return render(request, 'blog/post_form.html', {
        'post': post,
        'categories': categories
    })


# --- 5. 删除文章 ---
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author == request.user:
        post.delete()
    return redirect('blog:post_list')


# --- 6. 点赞接口 (AJAX/JSON) ---
@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    action = 'unliked'

    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        action = 'liked'
        if hasattr(request.user, 'experience'):
            request.user.experience += 3
            request.user.save()

    # 如果是 AJAX 请求则返回 Json
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok',
            'count': post.likes.count(),
            'action': action
        })

    return redirect('blog:post_detail', pk=pk)