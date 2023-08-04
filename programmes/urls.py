from django.urls import path
from . import views

urlpatterns = [
    path(
        "<path:numero_operation>",
        views.operation_conventions,
        name="operation_conventions",
    ),
]
