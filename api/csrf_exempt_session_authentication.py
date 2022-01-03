from rest_framework.authentication import SessionAuthentication

# should be replaced by a Token session with an endpoint to get it.
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening
