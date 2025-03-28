from django.conf import settings
from django.contrib.auth import get_user_model, login

UserModel = get_user_model()


class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Double check for security purpose
        if not settings.DEBUG or not settings.ENVIRONMENT == "development":
            return self.get_response(request)

        # Retrieve the mock cerbere user
        try:
            user = UserModel.objects.get(pk=settings.MOCK_CERBERE_USER_ID)
        except UserModel.DoesNotExist:
            return self.get_response(request)

        # Auto login for mock cerbere user
        login(request, user, backend="core.backends.MockCerbereBackend")

        # Disable readonly mode for staff and superuser
        if request.user.is_staff or request.user.is_superuser:
            request.session["readonly"] = False

        return self.get_response(request)
