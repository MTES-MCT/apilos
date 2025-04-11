from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerSplitView,
)

from apilos_settings.api.api_views import ApilosConfiguration, ConventionKPI
from programmes.api.operation_api_views import (
    DummyView,
    OperationCanceled,
    OperationClosed,
    OperationDetails,
)

urlpatterns = [
    # API authentication
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # Main configuration route
    path("config/", ApilosConfiguration.as_view()),
    # Main configuration route
    path("convention_kpi/", ConventionKPI.as_view()),
    # Operation details route
    path("operation/<str:numero_operation>/", OperationDetails.as_view()),
    # Operation close route
    path("close_operation/<str:numero_operation>/", OperationClosed.as_view()),
    # Opération cancel route
    path("cancel_operation/<str:numero_operation>/", OperationCanceled.as_view()),
    path("dummy/", DummyView.as_view()),
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
