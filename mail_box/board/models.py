from django.db import models

# Create your models here.

class Board(models.Model):
    author = models.ForeignKey('won_test.User', on_delete=models.CASCADE)
    title = models.CharField("제목", max_length=30)
    content = models.TextField("내용", max_length=120)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)


class BoardLike(models.Model):
    author = models.ForeignKey('won_test.User', on_delete=models.CASCADE)
    board = models.ForeignKey('board.Board', on_delete=models.CASCADE)


class BoardComment(models.Model):
    author = models.ForeignKey('won_test.User', on_delete=models.CASCADE)
    board = models.ForeignKey('board.Board', on_delete=models.CASCADE)
    content = models.TextField("내용", max_length=120)


class BoardCommentLike(models.Model):
    board_comment_author = models.ForeignKey('won_test.User', on_delete=models.CASCADE)
    board_comment = models.ForeignKey('board.BoardComment', on_delete=models.CASCADE)