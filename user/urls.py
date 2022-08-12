from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    path("", views.UserView.as_view(), name="user_view"),
    path("login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("usercheck", views.UserCheckView.as_view(), name="user_check_view"),
    path("user_certification", views.UserCertificationView.as_view(), name="user_certification_view"),
    path("profile", views.UserProfileView.as_view()),
    path("profile/category/", views.UserProfileCategoryView.as_view()),
    path("profile/category/<int:p_category>", views.UserProfileCategoryView.as_view()),
    path("report", views.ReportUserView.as_view()),
]
