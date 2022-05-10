from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerSplitView,
)
from core.api import api_views as core_api_views

urlpatterns = [
    # API authentication
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # Main configuration route
    path("config/", core_api_views.ApilosConfiguration.as_view()),
    # DRF spectacular
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema-ui/",
        SpectacularSwaggerSplitView.as_view(url_name="api-siap:schema"),
        name="schema-ui",
    ),
    path(
        "schema-redoc/",
        SpectacularRedocView.as_view(url_name="api-siap:schema"),
        name="schema-redoc",
    ),
]
