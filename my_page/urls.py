from django.urls import path

from . import views

urlpatterns = [
    path("my_letter", views.MyLetterView.as_view()),
    path("my_received_letter", views.MyRecievedLetterView.as_view()),
    path("my_not_read_letter", views.MyNotReadLetterView.as_view()),
    path("letter_review", views.LetterReviewView.as_view()),
]
