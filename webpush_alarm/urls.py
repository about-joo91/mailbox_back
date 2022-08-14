from django.urls import path

from . import views

urlpatterns = [
    path("", views.SendWebpushView.as_view()),
    path("test/", views.WebpushView.as_view()),
]
