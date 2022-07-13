from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# Create your models here.

############### ##################
class WorryCategory(models.Model):
    cate_name = models.CharField(max_length=30)


class Letter(models.Model):
    letter_author = models.ForeignKey("user.User", on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey("WorryCategory", on_delete=models.CASCADE)
    worryboard = models.OneToOneField("worry_board.WorryBoard", on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=30)
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)


class UserLetterTargetUser(models.Model):
    target_user = models.ForeignKey("user.User", on_delete=models.SET_NULL, null=True)
    letter = models.ForeignKey("Letter", on_delete=models.SET_NULL, null=True)


class LetterReview(models.Model):
    review_author = models.ForeignKey("user.User", on_delete=models.CASCADE)
    letter = models.ForeignKey("Letter", on_delete=models.CASCADE)
    grade = models.IntegerField()
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)


class LetterReviewLike(models.Model):
    review_id = models.ForeignKey("LetterReview", on_delete=models.CASCADE)
    user_id = models.ForeignKey("user.User", on_delete=models.CASCADE)
