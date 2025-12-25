from django.utils import timezone


class DailyLoginXPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            today = timezone.now().date()
            # 检查最后一次获得经验的日期
            if request.user.last_xp_date < today:
                # 触发每日首次登录奖励 20 经验
                request.user.add_experience(20)
                # add_experience 内部会更新 last_xp_date 并 save

        response = self.get_response(request)
        return response