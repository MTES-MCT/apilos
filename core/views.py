from typing import Any

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    INTERNAL_RESET_SESSION_TOKEN,
    PasswordContextMixin,
    PasswordResetConfirmView,
)
from django.core.mail import EmailMultiAlternatives
from django.http import HttpRequest
from django.views.generic.edit import FormView

from core.forms import ContactForm


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


class ContactView(FormView):
    form_class = ContactForm
    template_name = "contact.html"
    success_url = "/contact/"

    def form_valid(self, form):

        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Votre message a été envoyé avec succès",
        )
        EmailMultiAlternatives(
            from_email=form.cleaned_data["email"],
            #            to=["contact@apilos.beta.gouv.fr"],
            to=["nicolas@oudard.org"],
            subject=form.cleaned_data["subject"],
            body=(
                "MESSAGE LAISSÉ SUR L'INTERFACE <i>contact</i> D'APILOS<br><br>"
                f'DE: {form.cleaned_data["name"]}<br>'
                f'<br>MESSAGE: <br>{form.cleaned_data["message"]}'
            ),
        ).send()
        return super().form_valid(form)
