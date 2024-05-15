from django import forms

from users.type_models import EmailPreferences


class UserNotificationForm(forms.Form):
    preferences_email = forms.TypedChoiceField(
        required=True,
        initial=EmailPreferences.PARTIEL,
        label="Option d'envoi d'e-mail",
        choices=EmailPreferences.choices,
        error_messages={
            "required": "Les préférences emails sont obligatoires",
        },
    )


class UserForm(UserNotificationForm):
    username = forms.CharField(
        required=True,
        label="Nom d'utilisateur",
        max_length=150,
        min_length=1,
        error_messages={
            "required": "Le nom d'utilisateur est obligatoire",
            "min_length": "Le nom d'utilisateur est obligatoire",
            "max_length": "Le nom du programme ne doit pas excéder 150 caractères",
        },
    )
