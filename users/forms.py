from django import forms
from django.core.exceptions import ValidationError

from users.models import User


class UserForm(forms.Form):
    username = forms.CharField(
        required=True,
        max_length=150,
        min_length=1,
        error_messages={
            "required": "Le nom d'utilisateur est obligatoire",
            "min_length": "Le nom d'utilisateur est obligatoire",
            "max_length": "Le nom du programme ne doit pas excéder 150 caractères",
        },
    )

    first_name = forms.CharField(
        required=False,
        max_length=150,
        error_messages={
            "max_length": "Le prénom de l'utilisateur ne doit pas excéder 150 caractères",
        },
    )

    last_name = forms.CharField(
        required=False,
        max_length=150,
        error_messages={
            "max_length": "Le nom de l'utilisateur ne doit pas excéder 150 caractères",
        },
    )

    email = forms.EmailField(
        required=True,
        error_messages={
            "required": "L'email de l'utilisateur est obligatoire",
        },
    )

    administrateur_de_compte = forms.BooleanField(required=False)

    is_superuser = forms.BooleanField(required=False)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if (
            User.objects.filter(email=email)
            .exclude(username=self.cleaned_data["username"])
            .exists()
        ):
            raise ValidationError(
                "Le email du bailleur existe déjà, il doit-être unique"
            )
        return email


class AddBailleurForm(forms.Form):

    bailleur = forms.CharField(
        error_messages={
            "required": "Le nom d'utilisateur est obligatoire",
        }
    )
