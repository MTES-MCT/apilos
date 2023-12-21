import sys

from django.http import JsonResponse
from django.shortcuts import render

from siap.exceptions import SIAPException


def handle_error_500(request):
    exception_type, exception, _ = sys.exc_info()

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
            "exception_type": exception_type.__name__,
        },
        status=500,
    )
