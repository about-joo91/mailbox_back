from django.urls import path

from . import views

urlpatterns = [
    path("getinfo/", views.GetinfoView.as_view()),
    path("sendpush/", views.SendWebpushView.as_view()),
]
