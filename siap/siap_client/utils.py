import re
from typing import Tuple
import logging

from bailleurs.models import Bailleur
from instructeurs.models import Administration
from programmes.models import (
    Financement,
    Lot,
    Programme,
    TypeHabitat,
    TypeOperation,
    NatureLogement,
)
from users.models import User
from conventions.models import Convention

logger = logging.getLogger(__name__)


def get_or_create_conventions(operation: dict, user: User):
    try:
        bailleur = get_or_create_bailleur(operation["donneesMo"])
    except KeyError as ke:
        raise KeyError("Operation not well formatted, missing `donneesMo`") from ke
    try:
        administration = get_or_create_administration(operation["gestionnaire"])
    except KeyError as ke:
        raise KeyError("Operation not well formatted, missing `gestionnaire`") from ke
    try:
        programme = get_or_create_programme(operation, bailleur, administration)
    except KeyError as ke:
        raise KeyError(
            "Operation not well formatted, missing programme's informations"
        ) from ke
    try:
        (lots, conventions) = get_or_create_lots_and_conventions(
            operation, programme, user
        )
    except KeyError as ke:
        raise KeyError(
            "Operation not well formatted, missing lot and convention informations"
        ) from ke
    return (programme, lots, conventions)


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


def _address_interpretation(one_liner_adresse: str) -> Tuple[str]:
    adresse = one_liner_adresse
    code_postal = ville = ""
    five_digits = re.findall(r"\d{5}", one_liner_adresse)
    if five_digits:
        code_postal = five_digits[-1]
        (adresse, ville) = one_liner_adresse.split(five_digits[-1])
        ville = ville.strip(";, ") if ville is not None else ""
        adresse = adresse.strip(";, ") if adresse is not None else ""
    return (adresse, code_postal, ville)


def get_or_create_programme(
    programme_from_siap: dict, bailleur: Bailleur, administration: Administration
) -> Programme:
    if programme_from_siap["donneesOperation"]["sansTravaux"]:
        type_operation = TypeOperation.SANSTRAVAUX
        nature_logement = NatureLogement.LOGEMENTSORDINAIRES
    else:
        type_operation = _type_operation(
            programme_from_siap["donneesOperation"]["sousNatureOperation"]
        )
        nature_logement = _nature_logement(
            programme_from_siap["donneesOperation"]["natureLogement"]
        )
    (adresse, code_postal, ville) = _address_interpretation(
        programme_from_siap["donneesLocalisation"]["adresse"]
    )
    (programme, _) = Programme.objects.get_or_create(
        numero_galion=programme_from_siap["donneesOperation"]["numeroOperation"],
        bailleur=bailleur,
        administration=administration,
        defaults={
            "nom": programme_from_siap["donneesOperation"]["nomOperation"],
            "adresse": adresse,
            "code_postal": code_postal,
            "ville": ville,
            "code_insee_commune": programme_from_siap["donneesLocalisation"]["commune"][
                "codeInsee"
            ],
            "code_insee_departement": programme_from_siap["donneesLocalisation"][
                "departement"
            ]["codeInsee"],
            "code_insee_region": programme_from_siap["donneesLocalisation"]["region"][
                "codeInsee"
            ],
            "zone_abc": programme_from_siap["donneesLocalisation"]["zonage123"],
            "zone_123": programme_from_siap["donneesLocalisation"]["zonageABC"],
            "type_operation": type_operation,
            "nature_logement": nature_logement,
        },
    )
    return programme


def get_or_create_lots_and_conventions(
    operation: dict, programme: Programme, user: User
):
    logger.warning("====================")
    logger.warning("detailOperation : %s", operation["detailsOperation"])
    logger.warning("type_operation : %s", programme.type_operation)
    logger.warning("====================")
    lots = []
    conventions = []
    if (
        operation["detailsOperation"] is None
        and programme.type_operation == TypeOperation.SANSTRAVAUX
    ):
        (lot, _) = Lot.objects.get_or_create(
            programme=programme,
            bailleur=programme.bailleur,
            financement=Financement.SANS_FINANCEMENT,
            defaults={
                "type_habitat": TypeHabitat.MIXTE,
                "nb_logements": 0,
            },
        )
        lots.append(lot)
        (convention, _) = Convention.objects.get_or_create(
            programme=programme,
            bailleur=programme.bailleur,
            lot=lot,
            financement=Financement.SANS_FINANCEMENT,
            cree_par=user,
        )
        conventions.append(convention)
    else:
        for aide in operation["detailsOperation"]:
            (lot, _) = Lot.objects.get_or_create(
                programme=programme,
                bailleur=programme.bailleur,
                financement=_financement(aide["aide"]["code"]),
                defaults={
                    "type_habitat": _type_habitat(aide),
                    "nb_logements": _nb_logements(aide),
                },
            )
            lots.append(lot)
            (convention, _) = Convention.objects.get_or_create(
                programme=programme,
                bailleur=programme.bailleur,
                lot=lot,
                financement=_financement(aide["aide"]["code"]),
                cree_par=user,
            )
            conventions.append(convention)

    return (lots, conventions)


def _type_operation(type_operation_from_siap: str) -> TypeOperation:
    if type_operation_from_siap in ["CNE", TypeOperation.NEUF]:
        return TypeOperation.NEUF
    if type_operation_from_siap in ["AAM", TypeOperation.ACQUISAMELIORATION]:
        return TypeOperation.ACQUISAMELIORATION
    if type_operation_from_siap in ["AST", TypeOperation.ACQUISSANSTRAVAUX]:
        return TypeOperation.ACQUISSANSTRAVAUX
    return TypeOperation.SANSOBJET


def _nature_logement(nature_logement_from_siap: str) -> TypeOperation:
    nature_logement = NatureLogement.SANSOBJET
    if nature_logement_from_siap in ["LOO", NatureLogement.LOGEMENTSORDINAIRES]:
        nature_logement = NatureLogement.LOGEMENTSORDINAIRES
    if nature_logement_from_siap in ["ALF", NatureLogement.AUTRE]:
        nature_logement = NatureLogement.AUTRE
    if nature_logement_from_siap in ["HEB", NatureLogement.HEBERGEMENT]:
        nature_logement = NatureLogement.HEBERGEMENT
    if nature_logement_from_siap in ["RES", NatureLogement.RESISDENCESOCIALE]:
        nature_logement = NatureLogement.RESISDENCESOCIALE
    if nature_logement_from_siap in ["PEF", NatureLogement.PENSIONSDEFAMILLE]:
        nature_logement = NatureLogement.PENSIONSDEFAMILLE
    if nature_logement_from_siap in ["REA", NatureLogement.RESIDENCEDACCUEIL]:
        nature_logement = NatureLogement.RESIDENCEDACCUEIL
    if nature_logement_from_siap in ["REU", NatureLogement.RESIDENCEUNIVERSITAIRE]:
        nature_logement = NatureLogement.RESIDENCEUNIVERSITAIRE
    if nature_logement_from_siap in ["RHVS", NatureLogement.RHVS]:
        nature_logement = NatureLogement.RHVS
    return nature_logement


def _financement(code):
    if code in ["PLUS", Financement.PLUS]:
        return Financement.PLUS
    if code in ["PLAI", Financement.PLAI]:
        return Financement.PLAI
    if code in ["PLS", Financement.PLS]:
        return Financement.PLS
    if code in ["PLAI_ADP", Financement.PLAI_ADP]:
        return Financement.PLAI_ADP
    return code


def _type_habitat(aide: dict) -> TypeHabitat:
    if aide["logement"]["nbLogementsIndividuels"] is None:
        return TypeHabitat.COLLECTIF
    if aide["logement"]["nbLogementsCollectifs"] is None:
        return TypeHabitat.INDIVIDUEL
    return TypeHabitat.MIXTE


def _nb_logements(aide):
    return (aide["logement"]["nbLogementsIndividuels"] or 0) + (
        aide["logement"]["nbLogementsCollectifs"] or 0
    )
