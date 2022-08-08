from django.urls import path

from worry_board import views

urlpatterns = [
    path("", views.WorryBoardView.as_view()),
    path("<int:worry_board_id>", views.WorryBoardView.as_view()),
    path("request/<int:worry_board_id>", views.RequestMessageView.as_view()),
    path("request/pd/<int:request_message_id>", views.RequestMessageView.as_view()),
    path("request/detail_message/<int:request_message_id>", views.DetailWorryMessageView.as_view()),
    path("request/<str:case>", views.RequestMessageView.as_view()),
    path("request/accept/<int:request_message_id>/<str:case>", views.AcceptRequestMessageView.as_view()),
]
