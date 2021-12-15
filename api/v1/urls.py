from django.urls import include, path
from django.conf.urls import url
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from programmes.api import api_views

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

# router = routers.DefaultRouter()
# router.register(r"programme", views.ProgrammeViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("programmes/", api_views.programme_list),
    path("programmes/<str:uuid>/", api_views.programme_detail),
    #    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
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
