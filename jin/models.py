from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


# Create your models here.

############### ##################
class Woory_Category(models.Model):
    cate_name = models.CharField(max_length=30)


class Letter(models.Model):
    letter_author = models.ForeignKey(
        "won_test.User", on_delete=models.SET_NULL, null=True
    )
    category = models.ForeignKey("Woory_Category", on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    content = models.TextField()


class User_Letter_Target_User(models.Model):
    author = models.ForeignKey("won_test.User", on_delete=models.SET_NULL, null=True)
    target_user = models.ForeignKey("Letter", on_delete=models.SET_NULL, null=True)


class Letter_Review(models.Model):
    review_author = models.ForeignKey("won_test.User", on_delete=models.CASCADE)
    letter = models.ForeignKey("Letter", on_delete=models.CASCADE)
    grade = models.IntegerField()
    content = models.TextField()


class Letter_Review_Like(models.Model):
    review_id = models.ForeignKey("Letter_Review", on_delete=models.CASCADE)
    user_id = models.ForeignKey("won_test.User", on_delete=models.CASCADE)
