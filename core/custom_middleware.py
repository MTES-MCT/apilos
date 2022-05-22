from core.siap_client.client import SIAPClient


class CerbereSessionMiddleware:
    # pylint: disable=R0903
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # test if user is a siap user
        if request.user.is_cerbere_user():
            # test if habilitation is set for the current user
            if not request.session["habilitation_id"]:
                client = SIAPClient()
                try:
                    habilitation_id = request.GET.get("habilitation_id")
                except KeyError:
                    habilitation_id = 0

                # Set habilitation in session
                # Set habilitation in session
                response = client.get_habilitations(
                    user_login=request.user.cerbere_login,
                    habilitation_id=habilitation_id,
                )
                if response.code >= 200 and response.code < 300:
                    habilitations = response.json()
                    if habilitation_id and habilitation_id in map(
                        lambda x: x["id"], habilitations
                    ):
                        request.session["habilitation_id"] = habilitation_id
                        request.session["habilitations"] = habilitations
                    elif len(habilitations):
                        request.session["habilitation_id"] = habilitations[0]["id"]
                    else:
                        raise Exception("Pas d'habilitation associéé à l'utilisateur")
                # Set habilitation in session

        response = self.get_response(request)

        # print("custom middleware after response or previous middleware")

        return response
