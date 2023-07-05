import sys

from django.http import JsonResponse
from django.shortcuts import render


def handle_error_500(request):
    exception_type, _, _ = sys.exc_info()

    if request.path.startswith("/api-siap") and "SIAPException" in [
        t.__name__ for t in exception_type.mro()
    ]:
        return JsonResponse(
            {
                "error": "Une erreur est survenue lors de la communication avec la"
                + " plateforme SIAP. Veuillez réessayer ultérieurement."
            },
            status=500,
        )

    return render(
        request,
        "500.html",
        {
            "exception_type": exception_type.__name__,
            "is_siap_related": "SIAPException"
            in [t.__name__ for t in exception_type.mro()],
        },
        status=500,
    )
