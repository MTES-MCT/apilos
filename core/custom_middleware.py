from django.contrib.auth.models import Group
from django.conf import settings
from django.forms import model_to_dict
from django.http import HttpRequest
from bailleurs.models import Bailleur
from core.siap_client.client import SIAPClient
from instructeurs.models import Administration
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
                habilitations = response["habilitations"]
                request.session["habilitations"] = habilitations

                if habilitation_id in map(lambda x: x["id"], habilitations):
                    request.session["habilitation_id"] = habilitation_id
                    request.session["habilitation"] = list(
                        filter(lambda x: x.get("id") == habilitation_id, habilitations)
                    )[0]
                elif len(habilitations):
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

            for key in ["bailleur", "currently", "administration"]:
                request.user.siap_habilitation[key] = (
                    request.session[key] if key in request.session else None
                )
            # request.session["habilitation"]

        response = self.get_response(request)

        return response


def _find_or_create_entity(request: HttpRequest, habilitation: dict):
    request.session["currently"] = habilitation["groupe"]["profil"]["code"]
    if habilitation["groupe"]["profil"]["code"] == GroupProfile.SIAP_MO_PERS_MORALE:
        (bailleur, _) = Bailleur.objects.get_or_create(
            siren=habilitation["entiteMorale"]["siren"],
            defaults={
                "siret": habilitation["entiteMorale"]["siren"],
                "nom": habilitation["entiteMorale"]["nom"],
                "adresse": habilitation["entiteMorale"]["adresseLigne4"],
                "code_postal": habilitation["entiteMorale"]["adresseLigne6"][:5],
                "ville": habilitation["entiteMorale"]["adresseLigne6"][6:],
            },
        )
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
        Role.objects.get_or_create(
            typologie=TypeRole.BAILLEUR,
            bailleur=bailleur,
            user=request.user,
            group=Group.objects.get(name="bailleur"),
        )
    if habilitation["groupe"]["profil"]["code"] == GroupProfile.SIAP_SER_GEST:
        # create if not exists gestionnaire
        (administration, _) = Administration.objects.get_or_create(
            code=habilitation["gestionnaire"]["code"],
            defaults={
                "nom": habilitation["gestionnaire"]["libelle"],
            },
        )
        request.session["administration"] = model_to_dict(
            administration,
            fields=[
                "id",
                "uuid",
                "code",
                "nom",
            ],
        )
        Role.objects.get_or_create(
            typologie=TypeRole.INSTRUCTEUR,
            administration=administration,
            user=request.user,
            group=Group.objects.get(name="instructeur"),
        )
