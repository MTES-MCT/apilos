import sys
from django.http import JsonResponse

from django.shortcuts import render

from core.exceptions.types import (
    TimeoutSIAPException,
    UnauthorizedSIAPException,
    UnavailableServiceSIAPException,
    AssociationHLMSIAPException,
    InconsistentDataSIAPException,
    HabilitationSIAPException,
)


def handle_error_500(request):
    exception_type, _, _ = sys.exc_info()

    if exception_type in [
        UnauthorizedSIAPException,
        TimeoutSIAPException,
        UnavailableServiceSIAPException,
        AssociationHLMSIAPException,
        InconsistentDataSIAPException,
        HabilitationSIAPException,
    ]:
        if request.path.startswith("/api-siap"):
            return JsonResponse(
                {
                    "error": "Une erreur est survenue lors de la communication avec la"
                    + " plateforme SIAP. Veuillez réessayer ultérieurement."
                },
                status=500,
            )
        if exception_type == AssociationHLMSIAPException:
            return render(
                request,
                "500.html",
                {
                    "specific_error": """
                        <p class="fr-mb-3w">
                            Le module de conventionnement n'est accessible avec
                              l'habilitation « Association HLM ».
                        </p>
                    """,
                },
                status=500,
            )

        return render(
            request,
            "500.html",
            {
                "specific_error": """
                    <p class="fr-mb-3w">
                        Une erreur est survenue lors de la communication avec la plateforme SIAP.
                        Veuillez réessayer ultérieurement.
                    </p>
                """,
            },
            status=500,
        )
    return render(
        request,
        "500.html",
        {
            "specific_error": "",
        },
        status=500,
    )
