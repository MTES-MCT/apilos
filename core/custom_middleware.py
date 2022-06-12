import logging
from core.siap_client.client import SIAPClient, SIAPClientRemote
import http.client as http_client

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

                logging.warn(f"habilitation_id")
                if habilitation_id in map(lambda x: x["id"], habilitations):
                    logging.warn(f"habilitation_id in list")
                    request.session["habilitation_id"] = habilitation_id
                    request.session["habilitation"] = list(
                        filter(lambda x: x.get("id") == habilitation_id, habilitations)
                    )[0]
                elif len(habilitations):
                    logging.warn(f"habilitation_id not in list")
                    request.session["habilitation_id"] = habilitations[0]["id"]
                    request.session["habilitation"] = habilitations[0]
                else:
                    raise Exception("Pas d'habilitation associéé à l'utilisateur")
                # Set habilitation in session
#                _find_or_create_entity(request.session["habilitation"])

                response = SIAPClientRemote().get_menu(
                    user_login=request.user.cerbere_login,
                    habilitation_id=request.session["habilitation_id"],
                )
                request.session["menu"] = [] #response["menuItems"]

            request.user.siap_habilitation = request.session["habilitation"]

        response = self.get_response(request)

        return response


# def _find_or_create_entity(habilitation):
#     logging.warn(f"habilitation : {habilitation}")
