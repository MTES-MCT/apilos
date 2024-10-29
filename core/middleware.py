from django.conf import settings
from django.contrib.auth import get_user_model, login

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
