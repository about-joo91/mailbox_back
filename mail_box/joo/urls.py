from django.urls import path

from . import views


urlpatterns = [
    path('',views.MyPageView.as_view()),
]
