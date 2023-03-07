from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import formset_factory, BaseFormSet

from apilos_settings.models import Departement
from bailleurs.models import Bailleur

from users.models import User
from users.type_models import TypeRole, EmailPreferences


class UserForm(forms.Form):
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

    first_name = forms.CharField(
        required=False,
        label="Prénom",
        max_length=150,
        error_messages={
            "max_length": "Le prénom de l'utilisateur ne doit pas excéder 150 caractères",
        },
    )

    last_name = forms.CharField(
        required=False,
        label="Nom",
        max_length=150,
        error_messages={
            "max_length": "Le nom de l'utilisateur ne doit pas excéder 150 caractères",
        },
    )

    email = forms.EmailField(
        required=True,
        label="Email",
        error_messages={
            "required": "L'email de l'utilisateur est obligatoire",
        },
    )

    phoneNumberRegex = RegexValidator(regex=r"^\+*[0-9\s]{8,25}$")
    telephone = forms.CharField(
        required=False,
        validators=[phoneNumberRegex],
        max_length=25,
        label="Numéro de téléphone professionnel",
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

    is_superuser = forms.BooleanField(
        required=False,
        label="Super Utilisateur",
        help_text="Un super utilisateur a tous les droits",
    )

    preferences_email = forms.TypedChoiceField(
        required=True,
        initial=EmailPreferences.PARTIEL,
        label="Option d'envoi d'e-mail",
        choices=EmailPreferences.choices,
        error_messages={
            "required": "Les préférences emails sont obligatoires",
        },
    )

    filtre_departements = forms.ModelMultipleChoiceField(
        queryset=Departement.objects.all(),
        label="Filtrer par départements",
        help_text="Les programmes et conventions affichés à l'utilisateur seront filtrés"
        + " en utilisant la liste des départements ci-dessous",
        required=False,
    )

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
    def __init__(self, *args, bailleurs=None, administrations=None, **kwargs) -> None:
        self.declared_fields["bailleur"].choices = bailleurs
        self.declared_fields["administration"].choices = administrations
        super().__init__(*args, **kwargs)

    user_type = forms.ChoiceField(
        required=False, label="Type d'utilisateur", choices=TypeRole.choices
    )
    bailleur = forms.CharField(
        required=False,
        label="Entreprise bailleur",
    )
    administration = forms.CharField(
        required=False,
        label="Administration",
    )

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
        if bailleur_queryset:
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
    def __init__(self, *args, bailleurs=None, **kwargs) -> None:
        self.declared_fields["bailleur"].choices = bailleurs
        super().__init__(*args, **kwargs)

    bailleur = forms.CharField(
        label="",
        error_messages={
            "required": "Merci de sélectionner un Bailleur",
        },
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
