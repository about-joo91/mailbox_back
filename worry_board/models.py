from django.db import models

# Create your models here.


class WorryBoard(models.Model):
    author = models.ForeignKey("user.User", on_delete=models.CASCADE)
    category = models.ForeignKey("main_page.WorryCategory", on_delete=models.CASCADE)
    content = models.TextField("내용", max_length=90)
    create_date = models.DateTimeField(auto_now_add=True)


class RequestMessage(models.Model):
    author = models.ForeignKey("user.User", on_delete=models.CASCADE)
    request_message = models.TextField("요청 메세지", max_length=180)
    worry_board = models.ForeignKey("worry_board.WorryBoard", on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    request_status = models.ForeignKey("RequestStatus", on_delete=models.CASCADE, null=True)
    can_write_letter = models.BooleanField(default=False)


class RequestStatus(models.Model):
    status = models.CharField(max_length=20, unique=True)


# class DetailWorryMessage(models.Model):
#     content = models.TextField("상세내용", max_length=500)
#     request_message = models.ForeignKey("RequestMessage", on_delete=CASCADE)
