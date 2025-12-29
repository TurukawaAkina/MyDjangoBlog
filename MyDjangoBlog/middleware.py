from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 如果用户已经登录，直接放行
        if request.user.is_authenticated:
            return self.get_response(request)

        # 获取当前访问路径
        path = request.path_info

        # 核心修复：定义绝对不能拦截的白名单路径
        exempt_paths = [
            '/accounts/',  # 放行 allauth 所有路由（Google/GitHub 登录回调等）
            '/login/',  # 放行你的登录别名
            '/register/',  # 放行你的注册别名
            '/admin/',  # 放行后台
            '/static/',  # 放行静态文件
            '/media/',  # 放行媒体文件
        ]

        # 检查当前路径是否在白名单中
        if any(path.startswith(p) for p in exempt_paths):
            return self.get_response(request)

        # 如果不满足以上条件，重定向到登录页
        return redirect('account_login')