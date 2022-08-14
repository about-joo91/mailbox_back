from django.urls import path

from . import views

urlpatterns = [
    path("", views.SendWebpushView.as_view()),
    path("test/", views.WebpushView.as_view()),
    # path('save_information', save_info, name='save_webpush_info'),
    # path('', home),
    # path('send_push', send_push),
]
