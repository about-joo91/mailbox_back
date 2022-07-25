from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    path("", views.UserView.as_view()),
    path("login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile", views.UserProfileView.as_view()),
    path("profile/category/", views.UserProfileCategoryView.as_view()),
    path("profile/category/<int:p_category>", views.UserProfileCategoryView.as_view()),
    path("report", views.ReportUserView.as_view()),
]
