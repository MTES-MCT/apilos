import logging

from bailleurs.models import Bailleur
from instructeurs.models import Administration


def get_or_create_conventions(operation: dict):
    try:
        bailleur = get_or_create_bailleur(operation["donneesMo"])
    except KeyError as ke:
        raise KeyError("Operation not well formatted, missing `donneesMo`") from ke
    logging.warning(bailleur)
    try:
        administration = get_or_create_administration(operation["gestionnaire"])
    except KeyError as ke:
        raise KeyError("Operation not well formatted, missing `gestionnaire`") from ke
    logging.warning(administration)
    # Get or create programme
    # Get or create lot
    # Get or create conventions

    conventions = []
    return conventions


def get_or_create_bailleur(bailleur_from_siap: dict):
    # Nom
    if "nom" in bailleur_from_siap:
        nom = bailleur_from_siap["nom"]
    elif "raisonSociale" in bailleur_from_siap:
        nom = bailleur_from_siap["raisonSociale"]
    # Adresse
    if "adresseLigne4" in bailleur_from_siap:
        adresse = bailleur_from_siap["adresseLigne4"]
    elif "adresseL4Siege" in bailleur_from_siap:
        adresse = bailleur_from_siap["adresseL4Siege"]
    # code postal et ville
    if "adresseLigne6" in bailleur_from_siap:
        adresse = bailleur_from_siap["adresseLigne6"]
    elif "adresseL6Siege" in bailleur_from_siap:
        adresse = bailleur_from_siap["adresseL6Siege"]

    (bailleur, _) = Bailleur.objects.get_or_create(
        siren=bailleur_from_siap["siren"],
        defaults={
            "siret": bailleur_from_siap["siren"],
            "nom": nom,
            "adresse": adresse,
            "code_postal": adresse[:5],
            "ville": adresse[6:],
        },
    )
    return bailleur


def get_or_create_administration(administration_from_siap: dict):
    (administration, _) = Administration.objects.get_or_create(
        code=administration_from_siap["code"],
        defaults={
            "nom": administration_from_siap["libelle"],
        },
    )
    return administration
