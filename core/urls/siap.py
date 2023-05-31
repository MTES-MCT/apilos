import django_cas_ng.views
from django.conf import settings
from django.urls import include
from django.urls import path

from core.urls.common import urlpatterns

urlpatterns += [
    path(
        "api-siap/v0/", include(("api.siap.v0.urls", "api-siap"), namespace="api-siap")
    ),
    path(
        "accounts/cerbere-login",
        django_cas_ng.views.LoginView.as_view(),
        name="cas_ng_login",
    ),
    path(
        "accounts/cerbere-logout",
        django_cas_ng.views.LogoutView.as_view(),
        name="cas_ng_logout",
    ),
]

if "cerbere" in settings.INSTALLED_APPS:
    urlpatterns.extend(
        [
            path("cerbere/", include("cerbere.urls")),
        ]
    )
