from django.urls import path

from worry_board import views

urlpatterns = [
    path("", views.WorryBoardView.as_view()),
    path("<int:worry_board_id>", views.WorryBoardView.as_view()),
    path("request/<int:worry_board_id>", views.RequestMessageView.as_view()),
    path("request/pd/<int:request_message_id>", views.RequestMessageView.as_view()),
    path("request/<str:case>", views.RequestMessageView.as_view()),
]
