
from django.contrib.auth import get_user_model
from django.contrib.auth import login

class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        User = get_user_model()
        try:
            user = User.objects.get(pk=725)
            login(request, user, backend='core.backends.MockCerbereBackend')
        except User.DoesNotExist:
            pass

        response = self.get_response(request)
        return response