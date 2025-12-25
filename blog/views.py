from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Tag, Comment
from .forms import CommentForm  # 确保你已经创建了 CommentForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse  # 用于点赞 AJAX


def post_list(request):
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')

    posts = Post.objects.all().order_by('-created_at')

    if search_query:
        posts = posts.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))

    if category_id:
        posts = posts.filter(category_id=category_id)

    categories = Category.objects.all()
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    current_category = None
    if category_id:
        current_category = get_object_or_404(Category, id=category_id)

    return render(request, 'blog/post_list.html', {
        'posts': page_obj,
        'categories': categories,
        'search_query': search_query,
        'current_category': current_category
    })


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # 增加阅读量
    post.views += 1
    post.save(update_fields=['views'])

    # 获取顶级评论
    comments = post.comments.filter(parent=None).order_by('-created_at')

    # --- 处理评论逻辑 ---
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user

            # 处理回复功能 (parent_id)
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent_id = parent_id

            comment.save()

            # 增加经验值：评论 +5
            request.user.experience += 5
            request.user.save()

            return redirect('blog:post_detail', pk=post.pk)
    else:
        # 这一步非常重要：实例化空表单发送给模板，否则输入框不显示
        form = CommentForm()

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': form  # 传给模板
    })


@login_required
def post_create(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        banner = request.FILES.get('banner')

        post = Post.objects.create(
            title=title,
            content=content,
            author=request.user,
            category_id=category_id,
            banner=banner
        )
        return redirect('blog:post_detail', pk=post.pk)

    categories = Category.objects.all()
    return render(request, 'blog/post_form.html', {'categories': categories})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('blog:post_list')

    if request.method == "POST":
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        category_id = request.POST.get('category')
        if request.FILES.get('banner'):
            post.banner = request.FILES.get('banner')

        post.category_id = category_id
        post.save()
        return redirect('blog:post_detail', pk=post.pk)

    categories = Category.objects.all()
    return render(request, 'blog/post_form.html', {'post': post, 'categories': categories})


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author == request.user:
        post.delete()
    return redirect('blog:post_list')


@login_required
def post_like(request, pk):
    """
    修改点赞逻辑以支持 AJAX 异步请求
    """
    post = get_object_or_404(Post, pk=pk)
    action = 'unliked'

    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        action = 'liked'
        # 增加经验值：点赞 +3
        request.user.experience += 3
        request.user.save()

    # 如果是 AJAX 请求则返回 JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok',
            'count': post.total_likes(),  # 确保 Model 里有 total_likes 方法
            'action': action
        })

    # 否则普通重定向
    return redirect('blog:post_detail', pk=pk)