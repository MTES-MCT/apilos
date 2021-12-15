from django.urls import include, path
from django.conf.urls import url
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from programmes.api import api_views as programmes_api_views
from bailleurs.api import api_views as bailleurs_api_views

schema_view = get_schema_view(
    openapi.Info(
        title="APiLos API",
        default_version="v1",
        description="API REST de la plateforme de conventionnement APL APiLos",
        terms_of_service="/cgu",
        contact=openapi.Contact(email="contact@apilos.beta.gouv.fr"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # API authentication
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # Bailleurs ressource
    path("bailleurs/", bailleurs_api_views.BailleurList.as_view()),
    path("bailleurs/<str:uuid>/", bailleurs_api_views.BailleurDetail.as_view()),
    # Programmes ressource
    path("programmes/", programmes_api_views.ProgrammeList.as_view()),
    path("programmes/<str:uuid>/", programmes_api_views.ProgrammeDetail.as_view()),
    # SWAGGER documentation
    url(
        r"^documentation(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    url(
        r"^documentation/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    url(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]
