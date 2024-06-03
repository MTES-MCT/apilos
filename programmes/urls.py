from django.urls import path

from . import views

urlpatterns = [
    path(
        "<path:numero_operation>/seconde_vie/new",
        views.SecondeVieNewView.as_view(),
        name="seconde_vie_new",
    ),
    path(
        "<path:numero_operation>/seconde_vie/existing",
        views.SecondeVieExistingView.as_view(),
        name="seconde_vie_existing",
    ),
    path(
        "<path:numero_operation>",
        views.operation_conventions,
        name="operation_conventions",
    ),
]
