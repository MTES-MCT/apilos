from django.urls import include
from django.urls import path

from core.urls.common import urlpatterns
from core.views import SecurePasswordResetConfirmView

urlpatterns += [
    path("accounts/", include("django.contrib.auth.urls")),
    path(
        "accounts/reset/<uidb64>/<token>/",
        SecurePasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]
