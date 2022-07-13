from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

from django.conf import settings

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError("Users must have an username")
        user = self.model(
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username=username, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField("사용자 계정", max_length=50, unique=True)
    password = models.CharField("비밀번호", max_length=128)
    nickname = models.CharField("닉네임", max_length=20)
    create_date = models.DateTimeField("가입일", auto_now_add=True)
    update_date = models.DateTimeField("갱신일", auto_now=True)

    is_active = models.BooleanField(default=True)

    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = "username"

    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.username} / {self.nickname}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class UserProfile(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE)
    description = models.TextField(default='')
    mongle_level = models.IntegerField(default=0)
    mongle_grade = models.IntegerField(default=0)
    fullname = models.TextField(default='')
    profile_img = models.URLField(
        default="https://user-images.githubusercontent.com/55477835/178631292-f381c6e2-2541-4a2c-ba67-b5bb4369e3d0.jpeg"
    )


class UserProfileCategory(models.Model):
    user_profile = models.ForeignKey("UserProfile", on_delete=models.CASCADE)
    category = models.ForeignKey(
        "jin.WorryCategory", on_delete=models.SET_NULL, null=True
    )

class Report(models.Model):
    report_user = models.ForeignKey('User',on_delete=models.CASCADE)
    reported_user = models.ForeignKey('ReportedUser',on_delete=models.CASCADE)
    report_reason = models.CharField(max_length=150)

class ReportedUser(models.Model):
    user = models.ForeignKey('User',on_delete=models.CASCADE)