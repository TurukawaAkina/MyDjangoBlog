from django.utils import timezone

# 经验值配置
XP_PER_VIEW = 1
XP_PER_LIKE = 3
XP_PER_COMMENT = 5
DAILY_XP_CAP = 100


def add_experience(user, amount):
    if not user.is_authenticated:
        return

    today = timezone.now().date()

    # 重置每日经验
    if user.last_xp_date != today:
        user.daily_xp_earned = 0
        user.last_xp_date = today

    # 检查上限
    if user.daily_xp_earned >= DAILY_XP_CAP:
        user.save()
        return

    # 计算实际增加量
    actual_amount = amount
    if user.daily_xp_earned + amount > DAILY_XP_CAP:
        actual_amount = DAILY_XP_CAP - user.daily_xp_earned

    user.daily_xp_earned += actual_amount
    user.experience += actual_amount

    # 简单升级逻辑: 阈值 = (level * (level+1) / 2) * 100
    current_threshold = (user.level * (user.level + 1) // 2) * 100
    if user.experience >= current_threshold:
        user.level += 1

    user.save()