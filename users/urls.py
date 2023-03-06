from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),
    path(
        "update_currently",
        views.update_currently,
        name="update_currently",
    ),
    path("read_popup", views.update_user_popup, name="read_popup"),
]
