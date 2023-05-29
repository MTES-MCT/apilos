"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# pylint: disable=W0611

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from core.sitemaps import SITEMAPS

urlpatterns = [
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("hijack/", include("hijack.urls")),
    path("", include(("users.urls", "users"), namespace="users")),
    path(
        "conventions/",
        include(("conventions.urls", "conventions"), namespace="conventions"),
    ),
    path(
        "operations/",
        include(("programmes.urls", "programmes"), namespace="programmes"),
    ),
    path(
        "apilos_settings/",
        include(("apilos_settings.urls", "settings"), namespace="settings"),
    ),
    path("stats/", include(("stats.urls", "stats"), namespace="stats")),
    path("upload/", include(("upload.urls", "upload"), namespace="upload")),
    path("comments/", include(("comments.urls", "comments"), namespace="comments")),
    path("cgu", TemplateView.as_view(template_name="editorial/cgu.html"), name="cgu"),
    path(
        "accessibilite",
        TemplateView.as_view(template_name="editorial/accessibilite.html"),
        name="accessibilite",
    ),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": SITEMAPS},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("explorer/", include("explorer.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if "django_browser_reload" in settings.INSTALLED_APPS:
    urlpatterns.extend(
        [
            path("__reload__/", include("django_browser_reload.urls")),
        ]
    )

if "defender" in settings.INSTALLED_APPS:
    urlpatterns.extend(
        [
            path("admin/defender/", include("defender.urls")),
        ]
    )

if "debug_toolbar" in settings.INSTALLED_APPS:
    urlpatterns.extend(
        [
            path("__debug__/", include("debug_toolbar.urls")),
        ]
    )

if "cerbere" in settings.INSTALLED_APPS:
    urlpatterns.extend(
        [
            path("cerbere/", include("cerbere.urls")),
        ]
    )

handler500 = "core.exceptions.handler.handle_error_500"
