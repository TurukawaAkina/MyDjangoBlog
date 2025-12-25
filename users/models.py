from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class UserTitle(models.Model):
    name = models.CharField(max_length=50, verbose_name="头衔名称")
    color = models.CharField(max_length=20, default="#6c757d", verbose_name="徽章颜色代码")
    icon_class = models.CharField(max_length=50, default="bi-star-fill", verbose_name="图标类")

    def __str__(self):
        return self.name


class User(AbstractUser):
    nickname = models.CharField(max_length=50, blank=True, verbose_name='昵称')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', verbose_name='头像')
    bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')

    level = models.PositiveIntegerField(default=1, verbose_name="等级")
    experience = models.PositiveIntegerField(default=0, verbose_name="当前等级经验值")
    daily_xp_earned = models.PositiveIntegerField(default=0, verbose_name="今日获得经验")
    last_xp_date = models.DateField(default=timezone.now, verbose_name="最后获得经验日期")

    custom_title = models.ForeignKey(UserTitle, on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name="佩戴头衔")

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.nickname or self.username

    def add_experience(self, amount):
        today = timezone.now().date()
        if self.last_xp_date < today:
            self.daily_xp_earned = 0
            self.last_xp_date = today

        DAILY_LIMIT = 500
        if self.daily_xp_earned >= DAILY_LIMIT:
            return False, "上限"

        if self.daily_xp_earned + amount > DAILY_LIMIT:
            amount = DAILY_LIMIT - self.daily_xp_earned

        self.experience += amount
        self.daily_xp_earned += amount

        xp_needed = self.level * 100
        upgraded = False
        while self.experience >= xp_needed:
            self.experience -= xp_needed
            self.level += 1
            xp_needed = self.level * 100
            upgraded = True

        self.save()
        return upgraded, f"Gain {amount} XP"

    @property
    def current_level_max_xp(self):
        """当前等级升级所需总经验"""
        return self.level * 100

    @property
    def xp_progress(self):
        """当前等级进度百分比"""
        if self.current_level_max_xp == 0: return 0
        return int((self.experience / self.current_level_max_xp) * 100)

    @property
    def xp_to_next_level(self):
        """升级还需要的经验值"""
        return self.current_level_max_xp - self.experience