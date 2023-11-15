from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from pommento import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pommento.core.urls")),
    path("", include("pommento.auth.urls")),
    path("", include("pommento.billing.urls")),
]

if settings.DEBUG is True:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
        path("__reload__/", include("django_browser_reload.urls")),
    ]
