from typing import Tuple
from django.contrib.auth.models import Group
from django.conf import settings
from django.forms import model_to_dict
from django.http import HttpRequest
from siap.siap_client.utils import get_or_create_bailleur, get_or_create_administration
from siap.siap_client.client import SIAPClient
from users.models import Role, GroupProfile
from users.type_models import TypeRole


class CerbereSessionMiddleware:
    # pylint: disable=R0903
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
                client = SIAPClient.get_instance()

                # Set habilitation in session
                response = client.get_habilitations(
                    user_login=request.user.cerbere_login,
                    habilitation_id=habilitation_id,
                )
                habilitations = list(
                    filter(
                        lambda x: x["statut"] == "VALIDEE", response["habilitations"]
                    )
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
                _find_or_create_entity(request, request.session["habilitation"])

                if settings.NO_SIAP_MENU:
                    request.session["menu"] = None
                else:
                    response = client.get_menu(
                        user_login=request.user.cerbere_login,
                        habilitation_id=request.session["habilitation_id"],
                    )
                    request.session["menu"] = response["menuItems"]

            for key in ["bailleur", "currently", "administration", "role"]:
                request.user.siap_habilitation[key] = (
                    request.session[key] if key in request.session else None
                )

        response = self.get_response(request)

        return response


def _get_perimetre_geographique(from_habilitation: dict) -> Tuple[None, str]:
    perimetre_departement = perimetre_region = None
    if (
        "porteeTerritComp" in from_habilitation
        and "codePortee" in from_habilitation["porteeTerritComp"]
    ):
        if from_habilitation["porteeTerritComp"]["codePortee"] == "REG":
            perimetre_region = from_habilitation["porteeTerritComp"]["regComp"]["code"]
        if from_habilitation["porteeTerritComp"]["codePortee"] == "DEP":
            perimetre_departement = from_habilitation["porteeTerritComp"]["depComp"][
                "code"
            ]
    return (perimetre_departement, perimetre_region)


def _manage_role(from_habilitation, **kwargs):
    (perimetre_departement, perimetre_region) = _get_perimetre_geographique(
        from_habilitation
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


def _find_or_create_entity(request: HttpRequest, from_habilitation: dict):
    request.session["currently"] = from_habilitation["groupe"]["profil"]["code"]
    if from_habilitation["groupe"]["profil"]["code"] in [
        GroupProfile.SIAP_ADM_CENTRALE,
        GroupProfile.SIAP_SER_DEP,
        GroupProfile.SIAP_DIR_REG,
    ]:
        request.session["role"] = _manage_role(
            from_habilitation,
            typologie=TypeRole.ADMINISTRATEUR,
            user=request.user,
            group=Group.objects.get(name="administrateur"),
        )
    if (
        from_habilitation["groupe"]["profil"]["code"]
        == GroupProfile.SIAP_MO_PERS_MORALE
    ):
        bailleur = get_or_create_bailleur(from_habilitation["entiteMorale"])
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
            typologie=TypeRole.BAILLEUR,
            bailleur=bailleur,
            user=request.user,
            group=Group.objects.get(name="bailleur"),
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
            typologie=TypeRole.INSTRUCTEUR,
            administration=administration,
            user=request.user,
            group=Group.objects.get(name="instructeur"),
        )
