from django.urls import path

from . import views

urlpatterns = [
    path("main/", views.MainPageView.as_view()),
    path("letter/", views.LetterView.as_view()),
    path("review_like<int:board_id>", views.ReviewLikeView.as_view()),
]
