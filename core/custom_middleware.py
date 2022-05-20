class CerbereSessionMiddleware:
    # pylint: disable=R0903
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # print("custom middleware before next middleware/view")
        # print(request.headers)

        # # test if user is a siap user
        # if request.user.is_cerbere_user():
        #     # test if habilitation is set for the current user
        #     if request.session.

        response = self.get_response(request)

        # print("custom middleware after response or previous middleware")

        return response
