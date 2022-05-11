from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerSplitView,
)
from rest_framework_simplejwt import views as jwt_views
from apilos_settings.api.api_views import ApilosConfiguration


urlpatterns = [
    # API authentication
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # Main configuration route
    path("config/", ApilosConfiguration.as_view()),
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
    path("token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
]
