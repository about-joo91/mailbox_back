from django.db import models

# Create your models here.
class BoardLike(models.Model):
    post = models.ForeignKey("board.Board", on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)