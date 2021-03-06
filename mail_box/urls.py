from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("my_page/", include("my_page.urls")),
    path("board/", include("board.urls")),
    path("main_page/", include("main_page.urls")),
    path("worry_board/", include("worry_board.urls")),
    path("user/", include("user.urls")),
]
