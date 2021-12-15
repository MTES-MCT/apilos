from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r"user", views.UserViewSet)
router.register(r"programme", views.ProgrammeViewSet)
router.register(r"lot", views.LotViewSet)
router.register(r"logement", views.LogementViewSet)
router.register(r"logement_edd", views.LogementEDDViewSet)
router.register(r"annexe", views.AnnexeViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
