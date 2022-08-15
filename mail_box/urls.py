from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("my_page/", include("my_page.urls")),
    path("board/", include("board.urls")),
    path("main_page/", include("main_page.urls")),
    path("worry_board/", include("worry_board.urls")),
    path("user/", include("user.urls")),
    path("webpush_alarm/", include("webpush_alarm.urls")),
    path("webpush/", include("webpush.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
