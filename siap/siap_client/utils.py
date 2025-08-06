import logging
import re

from django.db import transaction

from bailleurs.models import Bailleur, NatureBailleur
from conventions.models import Convention
from conventions.models.pret import Pret
from instructeurs.models import Administration
from programmes.models import (
    Financement,
    Lot,
    NatureLogement,
    Programme,
    TypeHabitat,
    TypeOperation,
)
from programmes.models.choices import MAPPING_GARAGE_TYPE_TO_TYPOLOGIE
from programmes.models.models import TypeStationnement
from programmes.utils import diff_programme_duplication
from siap.exceptions import (
    BAILLEUR_IDENTIFICATION_MESSAGE,
    CONVENTION_NOT_NEEDED_MESSAGE,
    NOT_COMPLETED_MESSAGE,
    ConflictedOperationSIAPException,
    DuplicatedOperationSIAPException,
    SIAPException,
)
from users.models import User

logger = logging.getLogger(__name__)

ADDRESS_PC_CITY = "adresseLigne6"
ADDRESS_LINE_RAW = "adresseLigne4"
ADDRESS_CLEANED = "adresseLigne"

MAPPING_TYPOLOGIE_TO_NATURE_LOGEMENT = {
    "CADA": "HEB",
    "RU": "REU",
    "LLS": "LOO",
    "CPH": "HEB",
    "CHRS": "HEB",
    "RHVS_M": "RHVS",
    "RHVS_IG": "RHVS",
    "LF": "ALF",
    "LHSS": "HEB",
    "LAM": "HEB",
    "RELF": "ALF",
    # TODO: To be completed for seconde vies: MOUS, ETUDES, and GDV
    # FIXME: To be confirmed — added after an error occurred on an operation with the 'RELS' typology.
    # Check if 'REU' is the appropriate nature_logement.
    "RELS": "REU",
}


def get_or_create_programme_from_siap_operation(operation: dict) -> Programme:
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
            f"L'opération n'est pas bien formatée, lié à `donneesMo` : {operation}"
        ) from ke

    try:
        administration = get_or_create_administration(operation["gestionnaire"])
    except (KeyError, TypeError) as ke:
        raise KeyError(
            f"L'opération n'est pas bien formatée, lié à `gestionnaire` : {operation}"
        ) from ke

    try:
        programme = get_or_create_programme(operation, bailleur, administration)
    except (KeyError, TypeError) as ke:
        raise KeyError(
            "L'opération n'est pas bien formatée, manque les informations du"
            f" programme : {operation}"
        ) from ke
    return programme


def get_filtered_aides(operation: dict):
    if "donneesOperation" in operation and operation["donneesOperation"]["sansTravaux"]:
        return [Financement.SANS_FINANCEMENT]

    op_aides = [
        aide["aide"]["code"]
        for aide in operation["detailsOperation"]
        if "aide" in aide and "code" in aide["aide"]
    ]
    return [aide for aide in op_aides if aide in Financement.values]


def get_or_create_conventions_from_siap(operation: dict, user: User):
    filtered_op_aides = get_filtered_aides(operation)
    if len(filtered_op_aides) == 0:
        raise SIAPException(CONVENTION_NOT_NEEDED_MESSAGE)

    programme = get_or_create_programme_from_siap_operation(operation)

    try:
        (lots, conventions) = get_or_create_lots_and_conventions(
            operation, programme, user
        )
    except (KeyError, TypeError) as ke:
        raise SIAPException(NOT_COMPLETED_MESSAGE) from ke

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
        elif bailleur_from_siap.get("siret"):
            bailleur_siren = bailleur_from_siap["siret"]
        else:
            raise SIAPException(
                NOT_COMPLETED_MESSAGE + " ; " + BAILLEUR_IDENTIFICATION_MESSAGE
            )
    elif not (
        (bailleur_siren := bailleur_from_siap["siren"])
        if "siren" in bailleur_from_siap
        else None
    ):
        raise SIAPException(BAILLEUR_IDENTIFICATION_MESSAGE + " ; SIREN manquant")

    if (
        bailleur_siret := (
            (bailleur_from_siap["siret"])
            if (
                "siret" in bailleur_from_siap
                and bailleur_from_siap["siret"] is not None
            )
            else bailleur_siren
        )
    ) is None:
        raise SIAPException(BAILLEUR_IDENTIFICATION_MESSAGE + " ; SIREN manquant")

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
    if (
        "sansTravaux" in programme_from_siap["donneesOperation"]
        and programme_from_siap["donneesOperation"]["sansTravaux"]
    ):
        type_operation = TypeOperation.SANSTRAVAUX
    else:
        type_operation = _type_operation(
            programme_from_siap["donneesOperation"]["sousNatureOperation"]
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
        raise SIAPException(CONVENTION_NOT_NEEDED_MESSAGE)

    nature_logement = _get_nature_logement(programme_from_siap["donneesOperation"])
    try:
        (programme, _) = Programme.objects.get_or_create(
            numero_operation=programme_from_siap["donneesOperation"]["numeroOperation"],
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
    except Programme.MultipleObjectsReturned as exc:
        numero_operation = programme_from_siap["donneesOperation"]["numeroOperation"]

        diff = diff_programme_duplication(numero_operation=numero_operation)
        if len(diff):
            raise ConflictedOperationSIAPException(numero_operation, diff) from exc

        raise DuplicatedOperationSIAPException(
            numero_operation=numero_operation
        ) from exc

    # force nature_logement and administration
    programme.nature_logement = nature_logement
    programme.administration = administration
    # force type operation if it is sans travaux
    if type_operation == TypeOperation.SANSTRAVAUX:
        programme.type_operation = TypeOperation.SANSTRAVAUX
    programme.save()
    return programme


def create_subventions(subventions, financement, lot):
    for subvention in subventions:
        if subvention["type"] == financement:
            Pret.objects.create(
                lot=lot,
                montant=subvention["montant"] if subvention["montant"] else 0,
                autre="",
            )


def create_prets(prets, lot):
    for pret in prets:
        Pret.objects.create(
            lot=lot, montant=pret["montant"] if pret["montant"] else 0, autre=""
        )


def create_financements(operation, financement, lot):
    if "plansFinancement" in operation and operation["plansFinancement"]:
        for plan_financement in operation["plansFinancement"]:
            if plan_financement["codeAide"] == financement:
                create_prets(plan_financement["prets"], lot)
                create_subventions(plan_financement["subventions"], financement, lot)


def create_stationnements(aide_details, lot):
    loyers = aide_details.get("loyers", [])
    loyer_garages = loyers[0].get("loyerGarages", []) if loyers else []

    loyer_by_type = {garage["type"]: garage["loyer"] for garage in loyer_garages}

    for garage in aide_details.get("garages", []):
        nb_stationnements = (garage.get("nbGaragesIndividuels") or 0) + (
            garage.get("nbGaragesCollectifs") or 0
        )
        TypeStationnement.objects.create(
            lot=lot,
            typologie=MAPPING_GARAGE_TYPE_TO_TYPOLOGIE.get(garage.get("type")),
            nb_stationnements=nb_stationnements,
            loyer=loyer_by_type.get(garage.get("type"), 0),
        )


def get_or_create_lots_and_conventions_by_financement(
    operation: dict, programme: Programme, user: User, financement: Financement
):
    if (
        operation["detailsOperation"] is None
        and programme.type_operation == TypeOperation.SANSTRAVAUX
    ):
        convention = Convention.objects.create(
            programme=programme,
            cree_par=user,
        )
        Lot.objects.create(
            financement=Financement.SANS_FINANCEMENT,
            convention=convention,
        )
        return

    aide_details = next(
        (
            aide
            for aide in operation["detailsOperation"]
            if aide["aide"]["code"] == financement
        ),
        None,
    )
    if aide_details is None:
        return

    if financement == Financement.PLAI_ADP or financement not in Financement.values:
        return

    with transaction.atomic():
        convention = Convention.objects.create(
            programme=programme,
            cree_par=user,
        )
        lot = Lot.objects.create(
            financement=financement,
            convention=convention,
            type_habitat=_type_habitat(aide_details),
            nb_logements=_nb_logements(aide_details),
        )
        # create financement
        create_financements(operation, financement, lot)
        # Create garages if they exist in the aide_details
        create_stationnements(aide_details, lot)


def get_or_create_lots_and_conventions(
    operation: dict, programme: Programme, user: User
):
    lots = []
    conventions = []

    if (
        operation["detailsOperation"] is None
        and programme.type_operation == TypeOperation.SANSTRAVAUX
    ):
        convention = _get_or_create_convention(
            programme=programme,
            financement=Financement.SANS_FINANCEMENT,
            user=user,
        )
        (lot, _) = Lot.objects.get_or_create(
            financement=Financement.SANS_FINANCEMENT,
            convention=convention,
            defaults={
                "type_habitat": TypeHabitat.MIXTE,
                "nb_logements": 0,
            },
        )

        lots.append(lot)

        # When convention was created by SIAP through API and the user doesn't exist
        # the first user how access it will be the creator
        if convention.cree_par is None and user.id is not None:
            convention.user = user
            convention.save()
        conventions.append(convention)

    else:
        for aide in operation["detailsOperation"]:
            financement = _financement(aide["aide"]["code"])
            if financement is None:
                continue

            if (
                financement == Financement.PLAI_ADP
                or financement not in Financement.values
            ):
                continue

            # FIXME : Ici On a un soucis car On n'a plus de financement pour discriminer
            # les conventions, on a besoin de l'identifiant de l'aide pour le faire
            convention = _get_or_create_convention(
                programme=programme,
                financement=financement,
                user=user,
            )
            (lot, _) = Lot.objects.get_or_create(
                financement=financement,
                convention=convention,
                defaults={
                    "type_habitat": _type_habitat(aide),
                    "nb_logements": _nb_logements(aide),
                },
            )

            lots.append(lot)

    return (lots, conventions)


def _get_or_create_convention(programme: Programme, financement: str, user: User):

    conventions = Convention.objects.filter(
        programme=programme, lots__financement=financement
    )
    convention = None
    if conventions.count() == 0:
        convention = Convention.objects.create(
            programme=programme,
        )
    elif conventions.count() == 1:
        convention = conventions.first()
    else:
        raise Exception(
            "More than one convention found for the same programme/financement"
        )

    # When convention was created by SIAP through API and the user doesn't exist
    # the first user how access it will be the creator
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


def _get_nature_logement(donnees_operation: dict) -> NatureLogement:
    nature_logement = ""
    if "natureLogement" in donnees_operation and donnees_operation["natureLogement"]:
        nature_logement = donnees_operation["natureLogement"]
    elif (
        "typologie" in donnees_operation
        and donnees_operation["typologie"]
        in MAPPING_TYPOLOGIE_TO_NATURE_LOGEMENT.keys()
    ):
        nature_logement = MAPPING_TYPOLOGIE_TO_NATURE_LOGEMENT[
            donnees_operation["typologie"]
        ]
    return _nature_logement(nature_logement)


def _nature_logement(nature_logement_from_siap: str) -> NatureLogement:
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
        raise SIAPException(
            NOT_COMPLETED_MESSAGE
            + f" ; nature des logement : {nature_logement_from_siap}"
        )
    return nature_logement


def _financement(code) -> str | None:
    if code in Financement.values:
        return code
    return None


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
    if "logement" in aide and aide["logement"]:
        if (
            "nbLogementsIndividuels" in aide["logement"]
            and aide["logement"]["nbLogementsIndividuels"] is None
        ):
            return TypeHabitat.COLLECTIF
        if (
            "nbLogementsCollectifs" in aide["logement"]
            and aide["logement"]["nbLogementsCollectifs"] is None
        ):
            return TypeHabitat.INDIVIDUEL
    return TypeHabitat.MIXTE


def _nb_logements(aide):
    if "logement" in aide and aide["logement"]:
        return (aide["logement"]["nbLogementsIndividuels"] or 0) + (
            aide["logement"]["nbLogementsCollectifs"] or 0
        )
    return 0
