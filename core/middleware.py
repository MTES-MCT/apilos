from django.conf import settings
from django.contrib.auth import get_user_model, login

from core.utils import check_user_whitelist

UserModel = get_user_model()


class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            user = UserModel.objects.get(pk=settings.MOCK_CERBERE_USER_ID)
            login(request, user, backend="core.backends.MockCerbereBackend")
        except UserModel.DoesNotExist:
            pass

        response = self.get_response(request)
        return response


class LoginWhitelistMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            check_user_whitelist(request.user)

        return self.get_response(request)
