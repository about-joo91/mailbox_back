from unicodedata import category
from django.db import models

# Create your models here.


class WorryBoard(models.Model):
    author = models.ForeignKey("won_test.User", on_delete=models.CASCADE)
    category = models.ForeignKey("jin.WooryCategory", on_delete=models.CASCADE)
    content = models.TextField("내용", max_length=90)
    create_date = models.DateTimeField(auto_now_add=True)
