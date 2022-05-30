from core.siap_client.client import SIAPClient


class CerbereSessionMiddleware:
    # pylint: disable=R0903
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # test if user is a siap user
        if request.user.is_authenticated and request.user.is_cerbere_user():
            # test if habilitations are set for the current user
            # if not, get it from SIAPClient
            if "habilitations" not in request.session:

                # get habilitation_id from params if exists
                try:
                    habilitation_id = request.GET.get("habilitation_id")
                except KeyError:
                    if not request.session["habilitation_id"]:
                        habilitation_id = 0
                    else:
                        habilitation_id = request.session["habilitation_id"]

                client = SIAPClient.get_instance()

                # Set habilitation in session
                response = client.get_habilitations(
                    user_login=request.user.cerbere_login,
                    habilitation_id=habilitation_id,
                )
                habilitations = response["habilitations"]
                request.session["habilitations"] = habilitations

                if habilitation_id and habilitation_id in map(
                    lambda x: x["id"], habilitations
                ):
                    request.session["habilitation_id"] = habilitation_id
                elif len(habilitations):
                    request.session["habilitation_id"] = habilitations[0]["id"]
                else:
                    raise Exception("Pas d'habilitation associéé à l'utilisateur")
                # Set habilitation in session

            if "menu" not in request.session:
                client = SIAPClient.get_instance()
                response = client.get_menu(
                    user_login=request.user.cerbere_login,
                    habilitation_id=request.session["habilitation_id"],
                )
                request.session["menu"] = response["menuItems"]

        for key, value in request.session.items():
            print(f"{key} => {value}")

        response = self.get_response(request)

        # print("custom middleware after response or previous middleware")

        return response
