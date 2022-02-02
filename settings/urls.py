from django.urls import path
from . import views

urlpatterns = [
    path(
        "profile/",
        views.profile,
        name="profile",
    ),
    path(
        "",
        views.index,
        name="index",
    ),
    path(
        "users/",
        views.users,
        name="users",
    ),
    path(
        "bailleurs/",
        views.bailleurs,
        name="bailleurs",
    ),
    path(
        "administrations/",
        views.administrations,
        name="administrations",
    ),
    path(
        "administrations/<administration_uuid>",
        views.edit_administration,
        name="administration",
    ),
]
