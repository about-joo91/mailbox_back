from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


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
    username = models.CharField("사용자 계정", max_length=50, unique=True, blank=True)
    password = models.CharField("비밀번호", max_length=128, blank=True)
    nickname = models.CharField("닉네임", max_length=20, blank=True)
    received_letter_cnt = models.IntegerField(default=0)
    sent_letter_cnt = models.IntegerField(default=0)

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


class MongleLevel(models.Model):
    level = models.IntegerField(default=1)
    mongle_image = models.URLField(
        default="https://user-images.githubusercontent.com/55477835/183033723-5d7dc862-add3-4fc2-80e6-7cd5b90fce54.png"
    )


class MongleGrade(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE)
    grade = models.IntegerField(default=0)
    mongle_level = models.ForeignKey("MongleLevel", on_delete=models.SET_NULL, null=True)


class UserProfile(models.Model):
    user = models.OneToOneField("User", on_delete=models.CASCADE)
    description = models.TextField(default="")
    fullname = models.TextField(default="")
    categories = models.ManyToManyField("main_page.WorryCategory", through="UserProfileCategory")
    profile_img = models.URLField(
        default="https://user-images.githubusercontent.com/55477835/183034958-de0d010a-a105-459b-9d7b-915c04a882c7.png"
    )


class UserProfileCategory(models.Model):
    user_profile = models.ForeignKey("UserProfile", on_delete=models.CASCADE)
    category = models.ForeignKey("main_page.WorryCategory", on_delete=models.SET_NULL, null=True)


class Report(models.Model):
    report_user = models.ForeignKey("User", on_delete=models.CASCADE)
    reported_user = models.ForeignKey("ReportedUser", on_delete=models.CASCADE)
    report_reason = models.CharField(max_length=150)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["report_user", "reported_user"], name="only_one_report")]


class ReportedUser(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
