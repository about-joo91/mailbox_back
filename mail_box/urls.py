from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("won_test/", include("won_test.urls")),
    path("joo/", include("joo.urls")),
    path("board/", include("board.urls")),
    path("jin/", include("jin.urls"))
]
