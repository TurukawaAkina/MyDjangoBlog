from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Tag, Comment
from .forms import CommentForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# 文章列表
def post_list(request):
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    posts = Post.objects.all().order_by('-created_at')

    if search_query:
        posts = posts.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
    if category_id:
        posts = posts.filter(category_id=category_id)

    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    current_category = None
    if category_id:
        current_category = get_object_or_404(Category, id=category_id)

    return render(request, 'blog/post_list.html', {
        'posts': page_obj,
        'search_query': search_query,
        'current_category': current_category
    })

# 文章详情
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.views += 1
    post.save(update_fields=['views'])

    comments = post.comments.filter(parent=None).order_by('-created_at')

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

# --- 写文章视图 ---
@login_required
def post_create(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        banner = request.FILES.get('banner')

        # 简单的后端验证
        if title and content and category_id:
            post = Post.objects.create(
                title=title,
                content=content,
                author=request.user,
                category_id=category_id,
                banner=banner
            )
            # 发布文章奖励大额经验
            request.user.experience += 20
            request.user.save()
            return redirect('blog:post_detail', pk=post.pk)

    # 虽然有全局 categories，但表单页通常需要单独列出用于选择
    categories = Category.objects.all()
    return render(request, 'blog/post_form.html', {'categories': categories})

# 编辑文章
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
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
    return render(request, 'blog/post_form.html', {'post': post, 'categories': categories})

# 删除文章
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author == request.user:
        post.delete()
    return redirect('blog:post_list')

# 点赞接口
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