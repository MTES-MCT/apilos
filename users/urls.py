from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),
    path("read_popup", views.update_user_popup, name="read_popup"),
]
