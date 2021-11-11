from django.urls import path
from . import views

urlpatterns = [
    path("", views.add_comment, name="add_comment"),
    path("<comment_uuid>", views.update_comment, name="update_comment"),
]
