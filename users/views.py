from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm, UserProfileForm
from blog.models import Post
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # 必须加上 blog: 前缀
            return redirect('blog:post_list')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile_view(request):
    """
    个人中心视图
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    # 获取该作者的文章
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')

    return render(request, 'users/profile.html', {
        'form': form,
        'user_posts': user_posts
    })