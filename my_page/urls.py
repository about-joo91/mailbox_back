from django.urls import path

from . import views

urlpatterns = [
    path("my_letter", views.MyLetterView.as_view()),
    path("my_recieved_letter", views.MyRecievedLetterView.as_view()),
]
