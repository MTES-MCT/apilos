from typing import Any
from django.contrib.auth.views import (
    PasswordResetConfirmView,
    INTERNAL_RESET_SESSION_TOKEN,
    PasswordContextMixin,
)
from django.contrib.auth import login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest


class SecurePasswordResetConfirmView(PasswordResetConfirmView):
    """
    Redéfinition de la vue de confirmation du mot de passe afin d'éviter une erreur de
    clef manquante dans la session
    https://code.djangoproject.com/ticket/30952
    """

    def form_valid(self, form):
        user = form.save()
        # Ensure INTERNAL_RESET_SESSION_TOKEN actually is in session before trying to delete it
        if INTERNAL_RESET_SESSION_TOKEN in self.request.session:
            del self.request.session[INTERNAL_RESET_SESSION_TOKEN]

        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)

        return super(PasswordContextMixin).form_valid(form)


class SetupLoginRequiredMixin(LoginRequiredMixin):
    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        super().setup(request, *args, **kwargs)
        if request.user.is_authenticated:
            self.logged_in_setup(request, *args, **kwargs)

    def logged_in_setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        pass
