from django import forms
from django.core.exceptions import ValidationError

from users.models import User
from users.type_models import TypeRole


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
        same_users = User.objects.filter(email=email)
        if "username" in self.cleaned_data:
            same_users = same_users.exclude(username=self.cleaned_data["username"])

        if same_users.exists():
            raise ValidationError(
                "Le email de l'utilisateur existe déjà, il doit-être unique"
            )
        return email


class AddUserForm(UserForm):
    user_type = forms.ChoiceField(required=False, choices=TypeRole.choices)
    bailleur = forms.CharField(required=False)
    administration = forms.CharField(required=False)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError(
                "L'identifiant de l'utilisateur existe déjà, il doit-être unique"
            )
        return username

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get("user_type")
        is_superuser = cleaned_data.get("is_superuser")

        if not is_superuser:
            if not user_type:
                self.add_error(
                    "user_type",
                    ("Le type d'utilisateur est obligatoire"),
                )
            if user_type == "BAILLEUR":
                if not cleaned_data.get("bailleur"):
                    self.add_error(
                        "bailleur",
                        ("Le bailleur est obligatoire"),
                    )
            if user_type == "INSTRUCTEUR":
                if not cleaned_data.get("administration"):
                    self.add_error(
                        "administration",
                        ("L'administration est obligatoire"),
                    )

        user_type = cleaned_data.get("user_type")


class AddBailleurForm(forms.Form):

    bailleur = forms.CharField(
        error_messages={
            "required": "Merci de sélectionner un Bailleur",
        }
    )


class AddAdministrationForm(forms.Form):

    administration = forms.CharField(
        error_messages={
            "required": "Merci de sélectionner une Administration",
        }
    )
