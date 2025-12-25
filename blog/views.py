from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Tag, Comment
from .forms import CommentForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


def post_list(request):
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')

    posts = Post.objects.all().order_by('-created_at')

    if search_query:
        posts = posts.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))

    if category_id:
        posts = posts.filter(category_id=category_id)

    # 分页
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    current_category = None
    if category_id:
        current_category = get_object_or_404(Category, id=category_id)

    # 这里的 hot_posts 和 categories 已由 context_processor 全局提供
    return render(request, 'blog/post_list.html', {
        'posts': page_obj,
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

    # 处理评论逻辑
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user

            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent_id = parent_id

            comment.save()

            # 增加经验值
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

    # 注意：这里的 categories 也可以直接用全局的，但为了保持逻辑清晰暂留
    return render(request, 'blog/post_form.html')


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

    return render(request, 'blog/post_form.html', {'post': post})


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author == request.user:
        post.delete()
    return redirect('blog:post_list')


@login_required
def post_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    action = 'unliked'

    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        action = 'liked'
        request.user.experience += 3
        request.user.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok',
            'count': post.total_likes(),
            'action': action
        })

    return redirect('blog:post_detail', pk=pk)