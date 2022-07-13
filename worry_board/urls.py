from django.urls import path

from worry_board import views

urlpatterns = [
    path("", views.WorryBoardView.as_view()),
    path("<int:worry_board_id>", views.WorryBoardView.as_view()),
]
