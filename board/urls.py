from django.urls import path

from board import views

urlpatterns = [
    path('', views.BoardView.as_view()),
]
