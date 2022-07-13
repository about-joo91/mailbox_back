from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("joo/", include("joo.urls")),
    path("board/", include("board.urls")),
    path("jin/", include("jin.urls")),
    path("worry_board/", include("worry_board.urls")),
    path("user/",include("user.urls"))
]
