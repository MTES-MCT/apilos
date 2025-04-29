import sys

from django.http import JsonResponse
from django.shortcuts import render

from siap.exceptions import SIAPException


def handle_error_500(request):
    _, exception, _ = sys.exc_info()

    if request.path.startswith("/api-siap") and isinstance(exception, SIAPException):
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
            "is_siap_exception": isinstance(exception, SIAPException),
            "message": exception.__str__() if exception else "",
            "current_url": request.path,
            "habilitation_id": (
                request.session["habilitation_id"]
                if "habilitation_id" in request.session
                else None
            ),
        },
        status=500,
    )
