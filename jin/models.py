from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


# Create your models here.

############### ##################
class WooryCategory(models.Model):
    cate_name = models.CharField(max_length=30)


class Letter(models.Model):
    letter_author = models.ForeignKey(
        "won_test.User", on_delete=models.SET_NULL, null=True
    )
    category = models.ForeignKey("WooryCategory", on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)


class UserLetterTargetUser(models.Model):
    author = models.ForeignKey("won_test.User", on_delete=models.SET_NULL, null=True)
    target_user = models.ForeignKey("Letter", on_delete=models.SET_NULL, null=True)


class LetterReview(models.Model):
    review_author = models.ForeignKey("won_test.User", on_delete=models.CASCADE)
    letter = models.ForeignKey("Letter", on_delete=models.CASCADE)
    grade = models.IntegerField()
    content = models.TextField()


class LetterReviewLike(models.Model):
    review_id = models.ForeignKey("LetterReview", on_delete=models.CASCADE)
    user_id = models.ForeignKey("won_test.User", on_delete=models.CASCADE)
