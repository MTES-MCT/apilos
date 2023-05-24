from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path("login/", views.MockedCerbereLoginView.as_view(), name="mocked_cerbere_login"),
    path(
        "logout/",
        RedirectView.as_view(url="/", permanent=False),
        name="mocked_cerbere_logout",
    ),
]
