from typing import Tuple
from django.contrib.auth.models import Group
from django.conf import settings
from django.forms import model_to_dict
from django.http import HttpRequest
from bailleurs.models import NatureBailleur
from siap.siap_client.utils import get_or_create_bailleur, get_or_create_administration
from siap.siap_client.client import SIAPClient
from users.models import Role, GroupProfile
from users.type_models import TypeRole


class CerbereSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # test if user is a siap user
        if request.user.is_authenticated and request.user.is_cerbere_user():
            # test if habilitations are set for the current user
            # if not, get it from SIAPClient

            if (
                "habilitation_id" in request.GET
                or "habilitations" not in request.session
            ):

                # get habilitation_id from params if exists
                habilitation_id = 0
                if "habilitation_id" in request.GET:
                    habilitation_id = int(request.GET.get("habilitation_id"))
                elif "habilitation_id" in request.session:
                    habilitation_id = request.session["habilitation_id"]

                set_habilitation_in_session(
                    request, request.user.cerbere_login, habilitation_id
                )

                if settings.NO_SIAP_MENU:
                    request.session["menu"] = None
                else:
                    client = SIAPClient.get_instance()
                    response = client.get_menu(
                        user_login=request.user.cerbere_login,
                        habilitation_id=request.session["habilitation_id"],
                    )
                    request.session["menu"] = response["menuItems"]

            copy_session_habilitation_to_user(request)

        response = self.get_response(request)

        return response


def set_habilitation_in_session(
    request, cerbere_login, habilitation_id, session_only: bool = False
):
    client = SIAPClient.get_instance()
    response = client.get_habilitations(
        user_login=cerbere_login,
        habilitation_id=habilitation_id,
    )
    habilitations = list(
        filter(lambda x: x["statut"] == "VALIDEE", response["habilitations"])
    )
    request.session["habilitations"] = habilitations

    if habilitation_id in map(lambda x: x["id"], habilitations):
        request.session["habilitation_id"] = habilitation_id
        request.session["habilitation"] = list(
            filter(lambda x: x.get("id") == habilitation_id, habilitations)
        )[0]
    elif habilitations:
        request.session["habilitation_id"] = habilitations[0]["id"]
        request.session["habilitation"] = habilitations[0]
    else:
        raise Exception("Pas d'habilitation associéé à l'utilisateur")

    # Set habilitation in session
    _find_or_create_entity(
        request, request.session["habilitation"], session_only=session_only
    )


def copy_session_habilitation_to_user(request):
    for key in ["bailleur", "currently", "administration", "role"]:
        request.user.siap_habilitation[key] = (
            request.session[key] if key in request.session else None
        )


def _get_perimetre_geographique(from_habilitation: dict) -> Tuple[None, str]:
    perimetre_departement = perimetre_region = None
    if (
        "porteeTerritComp" in from_habilitation
        and "codePortee" in from_habilitation["porteeTerritComp"]
    ):
        if from_habilitation["porteeTerritComp"]["codePortee"] == "REG":
            if (
                "regComp" in from_habilitation["porteeTerritComp"]
                and "code" in from_habilitation["porteeTerritComp"]["regComp"]
            ):
                perimetre_region = from_habilitation["porteeTerritComp"]["regComp"][
                    "code"
                ]
        if from_habilitation["porteeTerritComp"]["codePortee"] == "DEP":
            if (
                "depComp" in from_habilitation["porteeTerritComp"]
                and "code" in from_habilitation["porteeTerritComp"]["depComp"]
            ):
                perimetre_departement = from_habilitation["porteeTerritComp"][
                    "depComp"
                ]["code"]
    return (perimetre_departement, perimetre_region)


def _manage_role(from_habilitation, session_only=False, **kwargs):
    (perimetre_departement, perimetre_region) = _get_perimetre_geographique(
        from_habilitation
    )
    if session_only:
        return model_to_dict(
            Role(
                **kwargs,
                perimetre_region=perimetre_region,
                perimetre_departement=perimetre_departement,
            )
        )
    Role.objects.filter(
        **kwargs,
        perimetre_region=perimetre_region,
        perimetre_departement=perimetre_departement,
    ).delete()
    (role, _) = Role.objects.get_or_create(
        **kwargs,
        perimetre_region=perimetre_region,
        perimetre_departement=perimetre_departement,
    )
    return model_to_dict(role)


def _find_or_create_entity(
    request: HttpRequest, from_habilitation: dict, session_only: bool = False
):
    request.session["bailleur"] = None
    request.session["administration"] = None
    request.session["role"] = None
    request.session["currently"] = from_habilitation["groupe"]["profil"]["code"]
    if from_habilitation["groupe"]["profil"]["code"] in [
        GroupProfile.SIAP_ADM_CENTRALE,
        GroupProfile.SIAP_SER_DEP,
        GroupProfile.SIAP_DIR_REG,
    ]:
        request.session["role"] = _manage_role(
            from_habilitation,
            session_only=session_only,
            typologie=TypeRole.ADMINISTRATEUR,
            user=request.user,
            group=Group.objects.get(name__iexact="administrateur"),
        )

    if from_habilitation["groupe"]["profil"]["code"] in [
        GroupProfile.SIAP_MO_PERS_MORALE,
        GroupProfile.SIAP_MO_PERS_PHYS,
    ]:
        bailleur_details = from_habilitation["entiteMorale"]
        if (
            from_habilitation["groupe"]["profil"]["code"]
            == GroupProfile.SIAP_MO_PERS_PHYS
        ):
            bailleur_details["siret"] = request.user.email
            bailleur_details["codeFamilleMO"] = NatureBailleur.PRIVES
        bailleur = get_or_create_bailleur(bailleur_details)
        request.session["bailleur"] = model_to_dict(
            bailleur,
            fields=[
                "id",
                "uuid",
                "siren",
                "nom",
            ],
        )
        # Manage Role following the habilitation["groupe"]["codeRole"]
        request.session["role"] = _manage_role(
            from_habilitation,
            session_only=session_only,
            typologie=TypeRole.BAILLEUR,
            bailleur=bailleur,
            user=request.user,
            group=Group.objects.get(name__iexact="bailleur"),
        )

    if from_habilitation["groupe"]["profil"]["code"] == GroupProfile.SIAP_SER_GEST:
        # create if not exists gestionnaire
        administration = get_or_create_administration(from_habilitation["gestionnaire"])
        request.session["administration"] = model_to_dict(
            administration,
            fields=[
                "id",
                "uuid",
                "code",
                "nom",
            ],
        )
        request.session["role"] = _manage_role(
            from_habilitation,
            session_only=session_only,
            typologie=TypeRole.INSTRUCTEUR,
            administration=administration,
            user=request.user,
            group=Group.objects.get(name__iexact="instructeur"),
        )
