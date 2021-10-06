from django.urls import path
from . import views

urlpatterns = [
    path("", views.upload_file, name="upload_file"),
    path(
        "<convention_uuid>/media/<uploaded_file_uuid>",
        views.display_file,
        name="display_file",
    ),
]
