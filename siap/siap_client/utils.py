import re
from typing import Tuple

from bailleurs.models import Bailleur, NatureBailleur
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


def get_or_create_conventions(operation: dict, user: User):
    try:
        # Waiting fix on SIAP
        # https://airtable.com/appqEzValO6eQoHbM/tblNIOUJttSKoH866/viwarZ7MJFl9MSfsi/recuXwXkRXzvssine?blocks=hide
        mo_data = (
            operation["entiteMorale"]
            if "entiteMorale" in operation
            else operation["donneesMo"]
        )
        bailleur = get_or_create_bailleur(mo_data)
    except (KeyError, TypeError) as ke:
        raise KeyError(
            f"Operation not well formatted, related to `donneesMo` : {operation}"
        ) from ke
    try:
        administration = get_or_create_administration(operation["gestionnaire"])
    except (KeyError, TypeError) as ke:
        raise KeyError(
            f"Operation not well formatted, related to `gestionnaire` : {operation}"
        ) from ke
    try:
        programme = get_or_create_programme(operation, bailleur, administration)
    except (KeyError, TypeError) as ke:
        raise KeyError(
            f"Operation not well formatted, missing programme's informations : {operation}"
        ) from ke
    try:
        (lots, conventions) = get_or_create_lots_and_conventions(
            operation, programme, user
        )
    except (KeyError, TypeError) as ke:
        raise KeyError(
            f"Operation not well formatted, missing lot and convention informations : {operation}"
        ) from ke
    return (programme, lots, conventions)


def get_or_create_bailleur(bailleur_from_siap: dict):
    # Nom
    if "nom" in bailleur_from_siap:
        nom = bailleur_from_siap["nom"]
    elif "raisonSociale" in bailleur_from_siap:
        nom = bailleur_from_siap["raisonSociale"]

    adresse = code_postal = ville = ""
    if "codePostal" in bailleur_from_siap:
        code_postal = bailleur_from_siap["codePostal"]

    if "ville" in bailleur_from_siap:
        ville = bailleur_from_siap["ville"]
    elif "adresseLigne6" in bailleur_from_siap:
        ville = bailleur_from_siap["adresseLigne6"].lstrip("1234567890 ")

    if "adresseLigne" in bailleur_from_siap:
        adresse = bailleur_from_siap["adresseLigne"]

    siret = (
        bailleur_from_siap["siret"]
        if "siret" in bailleur_from_siap
        else bailleur_from_siap["siren"]
    )

    (bailleur, is_created) = Bailleur.objects.get_or_create(
        siren=bailleur_from_siap["siren"],
        defaults={
            "siret": siret,
            "nom": nom,
            "adresse": adresse,
            "code_postal": code_postal,
            "ville": ville,
            "nature_bailleur": _get_nature_bailleur(bailleur_from_siap),
        },
    )
    # Workaround waiting fix on SIAP Side :
    # https://airtable.com/appqEzValO6eQoHbM/tblNIOUJttSKoH866/viwarZ7MJFl9MSfsi/recuXwXkRXzvssine?blocks=hide
    if not is_created and bailleur.nature_bailleur != _get_nature_bailleur(
        bailleur_from_siap
    ):
        bailleur.nature_bailleur = _get_nature_bailleur(bailleur_from_siap)
        bailleur.save()

    return bailleur


def get_or_create_administration(administration_from_siap: dict):
    (administration, _) = Administration.objects.get_or_create(
        code=administration_from_siap["code"],
        defaults={
            "nom": administration_from_siap["libelle"],
        },
    )
    return administration


def _get_address_from_locdata(loc_data: dict) -> Tuple[str]:
    if "adresseComplete" in loc_data:
        try:
            return (
                loc_data["adresseComplete"]["adresse"],
                loc_data["adresseComplete"]["codePostal"],
                loc_data["adresseComplete"]["commune"],
            )
        except KeyError:
            pass
    adresse = loc_data["adresse"]
    code_postal = ville = ""
    five_digits = re.findall(r"\d{5}", loc_data["adresse"])
    if five_digits:
        code_postal = five_digits[-1]
        (adresse, ville) = loc_data["adresse"].split(five_digits[-1])
        ville = ville.strip(";, ") if ville is not None else ""
        adresse = adresse.strip(";, ") if adresse is not None else ""
    return (adresse, code_postal, ville)


def get_or_create_programme(
    programme_from_siap: dict, bailleur: Bailleur, administration: Administration
) -> Programme:
    if (
        "sansTravaux" in programme_from_siap["donneesOperation"]
        and programme_from_siap["donneesOperation"]["sansTravaux"]
    ):
        type_operation = TypeOperation.SANSTRAVAUX
        nature_logement = NatureLogement.LOGEMENTSORDINAIRES
    else:
        type_operation = _type_operation(
            programme_from_siap["donneesOperation"]["sousNatureOperation"]
        )
        nature_logement = _nature_logement(
            programme_from_siap["donneesOperation"]["natureLogement"]
        )
    (adresse, code_postal, ville) = _get_address_from_locdata(
        programme_from_siap["donneesLocalisation"]
    )
    (programme, _) = Programme.objects.get_or_create(
        numero_galion=programme_from_siap["donneesOperation"]["numeroOperation"],
        bailleur=bailleur,
        administration=administration,
        parent=None,
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
    # force type opération = sans travaux
    if (
        type_operation == TypeOperation.SANSTRAVAUX
        and programme.type_operation != TypeOperation.SANSTRAVAUX
    ):
        programme.type_operation = TypeOperation.SANSTRAVAUX
        programme.save()
    return programme


def get_or_create_lots_and_conventions(
    operation: dict, programme: Programme, user: User
):
    lots = []
    conventions = []
    if (
        operation["detailsOperation"] is None
        and programme.type_operation == TypeOperation.SANSTRAVAUX
    ):
        (lot, _) = Lot.objects.get_or_create(
            programme=programme,
            financement=Financement.SANS_FINANCEMENT,
            defaults={
                "type_habitat": TypeHabitat.MIXTE,
                "nb_logements": 0,
            },
        )
        lots.append(lot)
        (convention, _) = Convention.objects.get_or_create(
            programme=programme,
            lot=lot,
            financement=Financement.SANS_FINANCEMENT,
            # When comes from SIAP through API, the user doesn't exist in DB
            defaults={
                "cree_par": (user if user.id else None),
            },
        )
        # When convention was created by SIAP through API and the user doesn't exist
        # the first user how access it will be the creator
        if convention.cree_par is None and user.id is not None:
            convention.user = user
            convention.save()
        conventions.append(convention)
    else:
        for aide in operation["detailsOperation"]:
            financement = _financement(aide["aide"]["code"])
            if financement == Financement.PLAI_ADP:
                continue
            (lot, _) = Lot.objects.get_or_create(
                programme=programme,
                financement=financement,
                defaults={
                    "type_habitat": _type_habitat(aide),
                    "nb_logements": _nb_logements(aide),
                },
            )
            lots.append(lot)
            (convention, _) = Convention.objects.get_or_create(
                programme=programme,
                lot=lot,
                financement=financement,
                # When comes from SIAP through API, the user doesn't exist in DB
                defaults={
                    "cree_par": (user if user.id else None),
                },
            )
            # When convention was created by SIAP through API and the user doesn't exist
            # the forst user how access it will be the creator
            if convention.cree_par is None and user.id is not None:
                convention.cree_par = user
                convention.save()

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


def _get_nature_bailleur(bailleur_from_siap):
    if "codeFamilleMO" in bailleur_from_siap:
        if bailleur_from_siap["codeFamilleMO"] in ["HLM", NatureBailleur.HLM]:
            return NatureBailleur.HLM
        if bailleur_from_siap["codeFamilleMO"] in ["SEM", NatureBailleur.SEM]:
            return NatureBailleur.SEM
        if bailleur_from_siap["codeFamilleMO"] in [
            "Bailleurs privés",
            NatureBailleur.PRIVES,
        ]:
            return NatureBailleur.PRIVES
    return NatureBailleur.AUTRES


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
