from django.urls import path

from . import views

urlpatterns = [
    path(
        "administrations/",
        views.administrations,
        name="administrations",
    ),
    path(
        "administrations/<administration_uuid>",
        views.EditAdministrationView.as_view(),
        name="edit_administration",
    ),
    path(
        "bailleurs/",
        views.bailleurs,
        name="bailleurs",
    ),
    path(
        "bailleurs/<bailleur_uuid>",
        views.EditBailleurView.as_view(),
        name="edit_bailleur",
    ),
    path(
        "profile/",
        views.UserProfileView.as_view(),
        name="profile",
    ),
    path(
        "users/",
        views.users,
        name="users",
    ),
]
