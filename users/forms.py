from django import forms
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.forms import BaseFormSet, formset_factory

from bailleurs.models import Bailleur
from users.models import User
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

    administrateur_de_compte = forms.BooleanField(
        required=False,
        label="Administrateur de compte",
        help_text=(
            "L'administrateur de compte peut gérer les utilisateurs de ses entités."
            + " Si vous renoncez à être administrateur,vous ne pourrez plus gérer les utilisateurs"
            + " de vos entités ou vous ré-attribuer les droits d'administration"
        ),
    )


class UserBailleurForm(forms.Form):
    first_name = forms.CharField(
        required=True,
        label="Prénom",
        max_length=150,
        error_messages={
            "max_length": "Le prénom de l'utilisateur ne doit pas excéder 150 caractères",
        },
    )

    last_name = forms.CharField(
        required=True,
        label="Nom",
        max_length=150,
        error_messages={
            "max_length": "Le nom de l'utilisateur ne doit pas excéder 150 caractères",
        },
    )

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

    email = forms.EmailField(
        required=True,
        label="Email",
        error_messages={
            "required": "L'email de l'utilisateur est obligatoire",
        },
    )

    bailleur = forms.ModelChoiceField(
        required=True,
        queryset=Bailleur.objects.none(),
        label="Entreprise bailleur",
    )

    def __init__(self, *args, bailleur_queryset=None, **kwargs) -> None:
        self.declared_fields["bailleur"].queryset = bailleur_queryset

        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():
            raise ValidationError(
                "L'adresse email de cet utilisateur existe déjà, elle doit-être unique"
            )
        return email

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise ValidationError(
                "L'identifiant de cet utilisateur existe déjà, il doit-être unique"
            )
        return username


class BaseUserBailleurFormSet(BaseFormSet):
    pass


UserBailleurFormSet = formset_factory(
    UserBailleurForm, formset=BaseUserBailleurFormSet, extra=0
)


class AddBailleurForm(forms.Form):
    def __init__(self, *args, bailleur_query: QuerySet, **kwargs) -> None:
        self.declared_fields["bailleur"].queryset = bailleur_query

        super().__init__(*args, **kwargs)

    bailleur = forms.ModelChoiceField(
        label="",
        error_messages={
            "required": "Merci de sélectionner un Bailleur",
        },
        queryset=Bailleur.objects.none(),
        to_field_name="uuid",
    )


class AddAdministrationForm(forms.Form):
    def __init__(self, *args, administrations=None, **kwargs) -> None:
        self.declared_fields["administration"].choices = administrations
        super().__init__(*args, **kwargs)

    administration = forms.CharField(
        label="",
        error_messages={
            "required": "Merci de sélectionner une Administration",
        },
    )
