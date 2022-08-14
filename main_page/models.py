from django.db import models

# Create your models here.


class WorryCategory(models.Model):
    cate_name = models.CharField(max_length=30, unique=True)


class Letter(models.Model):
    letter_author = models.ForeignKey("user.User", on_delete=models.SET_NULL, null=True)
    worryboard = models.OneToOneField("worry_board.WorryBoard", on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=30)
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    font_size = models.CharField(max_length=30, null=True)
    font_family = models.CharField(max_length=30, null=True)
    color = models.CharField(max_length=30, null=True)


class LetterReview(models.Model):
    review_author = models.ForeignKey("user.User", on_delete=models.CASCADE)
    letter = models.OneToOneField("Letter", on_delete=models.CASCADE)
    grade = models.IntegerField()
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    like_count = models.IntegerField(default=0)


class LetterReviewLike(models.Model):
    letter_review = models.ForeignKey("LetterReview", on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["letter_review", "user"], name="only_one_like")]
