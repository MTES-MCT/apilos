from django.http.request import HttpRequest

from users.models import User


class AuthenticatedHttpRequest(HttpRequest):
    user: User
