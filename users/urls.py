from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),
    path(
        "search/bailleur",
        views.search_bailleur,
        name="search_bailleur",
    ),
    path(
        "search/bailleur/<bailleur_uuid>/parent",
        views.search_parent_bailleur,
        name="search_parent_bailleur",
    ),
    path("read_popup", views.update_user_popup, name="read_popup"),
]
