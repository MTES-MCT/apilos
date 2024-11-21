"""
Étape Programme du formulaire par étape de la convention
"""

from django import forms

from programmes.models import TypeHabitat, TypeOperation


class ProgrammeMinimalForm(forms.Form):
    object_name = "programme"

    uuid = forms.UUIDField(
        required=False,
        label="Programme",
    )
    nom = forms.CharField(
        label="Nom",
        help_text=(
            "Indiquez uniquement le nom du programme. Le type de financement sera automatiquement"
            + " mentionné via notre logiciel"
        ),
        max_length=255,
        min_length=1,
        error_messages={
            "required": "Le nom du programme est obligatoire",
            "min_length": "Le nom du programme est obligatoire",
            "max_length": "Le nom du programme ne doit pas excéder 255 caractères",
        },
    )
    adresse = forms.CharField(
        label="Adresses du ou des bâtiments concernés par l'operation",
        help_text=(
            "Si le programme comporte plusieurs adresses (exemple : plusieurs bâtiments),"
            + " renseignez chaque adresse en allant à la ligne entre chaque nouvelle adresse"
        ),
        max_length=5000,
        min_length=1,
        error_messages={
            "required": "L'adresse est obligatoire",
            "min_length": "L'adresse est obligatoire",
            "max_length": "L'adresse ne doit pas excéder 5000 caractères",
        },
    )


class ProgrammeForm(ProgrammeMinimalForm):
    """ "
    Formulaire de l'opération pour la convention
    """

    code_postal = forms.CharField(
        label="Code postal",
        min_length=5,
        max_length=5,
        error_messages={
            "required": "Le code postal est obligatoire",
            "max_length": "Le code postal est une suite de 5 caractères",
            "min_length": "Le code postal est une suite de 5 caractères",
        },
    )
    ville = forms.CharField(
        label="Ville",
        max_length=255,
        error_messages={
            "required": "La ville est obligatoire",
            "max_length": "La ville ne doit pas excéder 255 caractères",
        },
    )
    type_habitat = forms.TypedChoiceField(
        required=False, label="Type d'habitat", choices=TypeHabitat.choices
    )
    type_operation = forms.TypedChoiceField(
        required=False, label="Type d'opération", choices=TypeOperation.choices
    )
    anru = forms.BooleanField(
        required=False,
        label="L'opération bénéficie d'un financement&nbsp;<strong>ANRU</strong>",
    )
    nb_locaux_commerciaux = forms.IntegerField(
        required=False,
        label="Locaux commerciaux",
    )
    nb_bureaux = forms.IntegerField(
        required=False,
        label="Bureaux",
    )
    autres_locaux_hors_convention = forms.CharField(
        required=False,
        label="Autres",
        max_length=5000,
        error_messages={
            "max_length": "L'information ne doit pas excéder 5000 caractères",
        },
    )
