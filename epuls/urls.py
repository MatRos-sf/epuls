import notifications.urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("super/admin/", admin.site.urls),
    # conflict with profile
    path("silk/", include("silk.urls", namespace="silk")),
    path("shouter/", include("shouter.urls")),
    path("", include("account.urls")),
    path("photo/", include("photo.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
    path(
        "inbox/notifications/", include(notifications.urls, namespace="notifications")
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# if settings.DEBUG:
#     urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
