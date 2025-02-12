"""
Étape Cadastre du formulaire par étape de la convention
"""

from django import forms
from django.forms import BaseFormSet, formset_factory


class ProgrammeCadastralForm(forms.Form):
    """
    Formulaire définissant les informations cadastrales et notariales générales liées à une convention
    """

    uuid = forms.UUIDField(
        required=False,
        label="Informations cadastrales",
    )
    permis_construire = forms.CharField(
        required=False,
        label="Numéro de permis construire",
        max_length=255,
        error_messages={
            "max_length": "Le permis de construire ne doit pas excéder 255 caractères",
        },
    )
    date_acte_notarie = forms.DateField(
        required=False,
        label="Date de l'acte notarié",
    )
    date_achevement_previsible = forms.DateField(
        required=False,
        label="Date d'achèvement previsible",
    )
    date_achat = forms.DateField(required=False, label="Date d'achat")
    date_achevement = forms.DateField(
        required=False,
        label="Date d'achèvement ou d'obtention de certificat de conformité",
    )

    date_autorisation_hors_habitat_inclusif = forms.DateField(
        required=False,
        label="",
    )
    date_convention_location = forms.DateField(
        required=False,
        label="",
    )

    date_residence_argement_gestionnaire_intermediation = forms.DateField(
        required=False,
        label="",
    )
    departement_residence_argement_gestionnaire_intermediation = forms.CharField(
        required=False,
        label="",
        max_length=255,
        error_messages={
            "max_length": "Le département ne doit pas excéder 255 caractères",
        },
    )
    ville_signature_residence_agrement_gestionnaire_intermediation = forms.CharField(
        required=False,
        label="",
        max_length=255,
        error_messages={
            "max_length": "La ville de signatures ne doit pas excéder 255 caractères",
        },
    )

    vendeur = forms.CharField(
        required=False,
        label="Vendeur",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )
    vendeur_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images sont acceptés dans la limite de 100 Mo",
    )
    acquereur = forms.CharField(
        required=False,
        label="Acquéreur",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )
    acquereur_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images sont acceptés dans la limite de 100 Mo",
    )
    reference_notaire = forms.CharField(
        required=False,
        label="Référence du notaire",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )
    reference_notaire_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images sont acceptés dans la limite de 100 Mo",
    )
    reference_publication_acte = forms.CharField(
        required=False,
        label="Référence de publication de l'acte",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )
    reference_publication_acte_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images sont acceptés dans la limite de 100 Mo",
    )
    acte_de_propriete = forms.CharField(
        required=False,
        label="Acte de propriété / Acte notarial",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )
    acte_de_propriete_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images et pdf sont acceptés dans la limite de 100 Mo",
    )
    certificat_adressage = forms.CharField(
        required=False,
        label="Certificat d'adressage / Autres",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )
    certificat_adressage_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images et pdf sont acceptés dans la limite de 100 Mo",
    )
    effet_relatif = forms.CharField(
        required=False,
        label="Effet relatif",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )
    effet_relatif_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images sont acceptés dans la limite de 100 Mo",
    )
    reference_cadastrale = forms.CharField(
        required=False,
        label="Références cadastrales",
        max_length=5000,
        error_messages={
            "max_length": "Le message ne doit pas excéder 5000 caractères",
        },
    )
    reference_cadastrale_files = forms.CharField(
        required=False,
        help_text="Les fichiers de type images sont acceptés dans la limite de 100 Mo",
    )


class ReferenceCadastraleForm(forms.Form):
    """
    Formulaire référence cadastrale formant la liste des références cadastrales d'une convention :
      une ligne du tableau des références cadastrales
    """

    uuid = forms.UUIDField(
        required=False,
        label="Référence Cadastrale",
    )
    section = forms.CharField(
        required=True,
        label="",
        max_length=255,
        error_messages={
            "required": "La section est obligatoire",
            "max_length": "Le message ne doit pas excéder 255 caractères",
        },
    )
    numero = forms.CharField(
        required=True,
        label="",
        max_length=255,
        error_messages={
            "required": "Le numéro est obligatoire",
        },
    )
    lieudit = forms.CharField(
        required=True,
        label="",
        max_length=255,
        error_messages={
            "required": "Le lieudit est obligatoire",
            "max_length": "Le lieudit ne doit pas excéder 255 caractères",
        },
    )
    surface = forms.CharField(
        required=True,
        label="",
        max_length=255,
        error_messages={
            "required": "La surface est obligatoire",
            "max_length": "La surface ne doit pas excéder 255 caractères",
        },
    )
    autre = forms.CharField(
        required=False,
        label="",
        max_length=255,
        error_messages={
            "max_length": "Le message ne doit pas excéder 255 caractères",
        },
    )


class BaseReferenceCadastraleFormSet(BaseFormSet):
    pass


ReferenceCadastraleFormSet = formset_factory(
    ReferenceCadastraleForm, formset=BaseReferenceCadastraleFormSet, extra=0
)
