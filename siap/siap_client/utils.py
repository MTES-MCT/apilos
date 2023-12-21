import logging
import re

from bailleurs.models import Bailleur, NatureBailleur
from conventions.models import Convention, ConventionStatut
from instructeurs.models import Administration
from programmes.models import (
    Financement,
    Lot,
    NatureLogement,
    Programme,
    TypeHabitat,
    TypeOperation,
)
from programmes.utils import diff_programme_duplication
from siap.exceptions import (
    DuplicatedOperationSIAPException,
    InconsistentDataSIAPException,
    NoConventionForOperationSIAPException,
    NotHandledBailleurPriveSIAPException,
    OperationToRepairSIAPException,
)
from users.models import User

logger = logging.getLogger(__name__)

ADDRESS_PC_CITY = "adresseLigne6"
ADDRESS_LINE_RAW = "adresseLigne4"
ADDRESS_CLEANED = "adresseLigne"


def get_or_create_conventions(operation: dict, user: User):
    if operation["detailsOperation"]:
        op_aides = [
            aide["aide"]["code"]
            for aide in operation["detailsOperation"]
            if "aide" in aide and "code" in aide["aide"]
        ]
        filtered_op_aides = [aide for aide in op_aides if aide in Financement.values]
        if len(filtered_op_aides) == 0:
            raise NoConventionForOperationSIAPException()

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
    nom = _get_bailleur_nom(bailleur_from_siap)
    code_postal = _get_bailleur_code_postal(bailleur_from_siap)
    ville = _get_bailleur_ville(bailleur_from_siap)
    adresse = _get_bailleur_adresse(bailleur_from_siap)
    nature_bailleur = _get_nature_bailleur(bailleur_from_siap)

    if nature_bailleur in [
        "Bailleurs privés",
        NatureBailleur.PRIVES,
    ]:
        if "email" in bailleur_from_siap and bailleur_from_siap["email"]:
            bailleur_siren = bailleur_from_siap["email"]
        else:
            raise NotHandledBailleurPriveSIAPException(
                "The « Bailleurs privés » type of bailleur is not handled yet"
            )
    elif not (
        (bailleur_siren := bailleur_from_siap["siren"])
        if "siren" in bailleur_from_siap
        else None
    ):
        raise InconsistentDataSIAPException(
            "Missing Bailleur siren (can't be empty or null), bailleur can't be get or created"
        )

    if (
        bailleur_siret := (bailleur_from_siap["siret"])
        if "siret" in bailleur_from_siap
        else bailleur_siren
    ) is None:
        raise InconsistentDataSIAPException(
            "Missing Bailleur siret, can't get or create it"
        )

    (bailleur, is_created) = Bailleur.objects.get_or_create(
        siren=bailleur_siren,
        defaults={
            "siret": bailleur_siret,
            "nom": nom,
            "adresse": adresse,
            "code_postal": code_postal,
            "ville": ville,
            "nature_bailleur": nature_bailleur,
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


def _get_bailleur_nom(bailleur_from_siap: dict) -> str:
    if "nom" in bailleur_from_siap:
        return bailleur_from_siap["nom"]
    if "raisonSociale" in bailleur_from_siap:
        return bailleur_from_siap["raisonSociale"]
    return ""


def _get_bailleur_code_postal(bailleur_from_siap: dict) -> str:
    if "codePostal" in bailleur_from_siap:
        return bailleur_from_siap["codePostal"]
    if ADDRESS_PC_CITY in bailleur_from_siap and bailleur_from_siap[ADDRESS_PC_CITY]:
        return (
            bailleur_from_siap[ADDRESS_PC_CITY][:5]
            if bailleur_from_siap[ADDRESS_PC_CITY][:5].isnumeric()
            else ""
        )
    return ""


def _get_bailleur_ville(bailleur_from_siap: dict) -> str:
    if "ville" in bailleur_from_siap:
        return bailleur_from_siap["ville"]
    if ADDRESS_PC_CITY in bailleur_from_siap and bailleur_from_siap[ADDRESS_PC_CITY]:
        return bailleur_from_siap[ADDRESS_PC_CITY].lstrip("1234567890 ")
    return ""


def _get_bailleur_adresse(bailleur_from_siap: dict) -> str:
    if ADDRESS_CLEANED in bailleur_from_siap:
        return bailleur_from_siap[ADDRESS_CLEANED]
    if ADDRESS_LINE_RAW in bailleur_from_siap:
        return bailleur_from_siap[ADDRESS_LINE_RAW]
    return ""


def get_or_create_administration(administration_from_siap: dict):
    (administration, _) = Administration.objects.get_or_create(
        code=administration_from_siap["code"],
        defaults={
            "nom": administration_from_siap["libelle"],
        },
    )
    return administration


def _get_address_from_locdata(loc_data: dict) -> tuple[str]:
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
    nature_logement = NatureLogement.LOGEMENTSORDINAIRES
    if (
        "sansTravaux" in programme_from_siap["donneesOperation"]
        and programme_from_siap["donneesOperation"]["sansTravaux"]
    ):
        type_operation = TypeOperation.SANSTRAVAUX
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

    if type_operation != TypeOperation.SANSTRAVAUX and (
        "detailsOperation" not in programme_from_siap
        or [
            aide["aide"]["code"]
            for aide in programme_from_siap["detailsOperation"]
            if aide["aide"]["code"] in Financement.values
        ]
        == []
    ):
        raise NoConventionForOperationSIAPException()

    try:
        (programme, _) = Programme.objects.get_or_create(
            numero_galion=programme_from_siap["donneesOperation"]["numeroOperation"],
            parent=None,
            defaults={
                "bailleur": bailleur,
                "administration": administration,
                "nom": programme_from_siap["donneesOperation"]["nomOperation"],
                "adresse": adresse,
                "code_postal": code_postal,
                "ville": ville,
                "code_insee_commune": programme_from_siap["donneesLocalisation"][
                    "commune"
                ]["codeInsee"],
                "code_insee_departement": programme_from_siap["donneesLocalisation"][
                    "departement"
                ]["codeInsee"],
                "code_insee_region": programme_from_siap["donneesLocalisation"][
                    "region"
                ]["codeInsee"],
                "zone_abc": programme_from_siap["donneesLocalisation"]["zonage123"],
                "zone_123": programme_from_siap["donneesLocalisation"]["zonageABC"],
                "type_operation": type_operation,
                "nature_logement": nature_logement,
            },
        )
    except Programme.MultipleObjectsReturned:
        numero_operation = programme_from_siap["donneesOperation"]["numeroOperation"]

        diff = diff_programme_duplication(numero_operation=numero_operation)
        if len(diff):
            raise OperationToRepairSIAPException(numero_operation=numero_operation)

        raise DuplicatedOperationSIAPException(numero_operation=numero_operation)

    # force nature_logement and administration
    programme.nature_logement = nature_logement
    programme.administration = administration
    # force type operation if it is sans travaux
    if type_operation == TypeOperation.SANSTRAVAUX:
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
        (convention, _) = Convention.objects.exclude(
            statut=ConventionStatut.ANNULEE.label,
        ).get_or_create(
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
            if (
                financement == Financement.PLAI_ADP
                or financement not in Financement.values
            ):
                continue
            (lot, _) = Lot.objects.get_or_create(
                programme=programme,
                financement=financement,
                defaults={
                    "type_habitat": _type_habitat(aide),
                    "nb_logements": _nb_logements(aide),
                },
            )

            convention = _create_convention_from_lot(lot, user)
            lots.append(lot)
    return (lots, conventions)


def _create_convention_from_lot(lot: Lot, user: User):
    (convention, _) = Convention.objects.exclude(
        statut=ConventionStatut.ANNULEE.label,
    ).get_or_create(
        programme=lot.programme,
        lot=lot,
        financement=lot.financement,
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
    return convention


def _type_operation(type_operation_from_siap: str) -> TypeOperation:
    if type_operation_from_siap in ["CNE", TypeOperation.NEUF]:
        return TypeOperation.NEUF
    if type_operation_from_siap in ["AAM", TypeOperation.ACQUISAMELIORATION]:
        return TypeOperation.ACQUISAMELIORATION
    if type_operation_from_siap in ["AST", TypeOperation.ACQUISSANSTRAVAUX]:
        return TypeOperation.ACQUISSANSTRAVAUX
    return TypeOperation.SANSOBJET


def _nature_logement(nature_logement_from_siap: str) -> TypeOperation:
    if nature_logement_from_siap in ["ALF", NatureLogement.AUTRE]:
        nature_logement = NatureLogement.AUTRE
    elif nature_logement_from_siap in ["HEB", NatureLogement.HEBERGEMENT]:
        nature_logement = NatureLogement.HEBERGEMENT
    elif nature_logement_from_siap in ["RES", NatureLogement.RESISDENCESOCIALE]:
        nature_logement = NatureLogement.RESISDENCESOCIALE
    elif nature_logement_from_siap in ["PEF", NatureLogement.PENSIONSDEFAMILLE]:
        nature_logement = NatureLogement.PENSIONSDEFAMILLE
    elif nature_logement_from_siap in ["REA", NatureLogement.RESIDENCEDACCUEIL]:
        nature_logement = NatureLogement.RESIDENCEDACCUEIL
    elif nature_logement_from_siap in ["REU", NatureLogement.RESIDENCEUNIVERSITAIRE]:
        nature_logement = NatureLogement.RESIDENCEUNIVERSITAIRE
    elif nature_logement_from_siap in ["RHVS", NatureLogement.RHVS]:
        nature_logement = NatureLogement.RHVS
    elif nature_logement_from_siap in ["LOO", NatureLogement.LOGEMENTSORDINAIRES]:
        nature_logement = NatureLogement.LOGEMENTSORDINAIRES
    else:
        raise InconsistentDataSIAPException(
            f"The NatureLogement value coming from SIAP is missing or unexpected : {nature_logement_from_siap}"
        )
    return nature_logement


def _financement(code):
    if code in ["PLUS_CD", Financement.PLUS_CD]:
        return Financement.PLUS_CD
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
