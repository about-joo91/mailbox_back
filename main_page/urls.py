from django.urls import path

from . import views

urlpatterns = [
    path("main/", views.MainPageView.as_view()),
    path("letter/", views.LetterView.as_view()),
    path("letter/<int:letter_id>", views.LetterisReadView.as_view()),
    path("review_like<int:letter_review_id>", views.ReviewLikeView.as_view()),
    path("review/like_get", views.LikeisGet.as_view()),
]