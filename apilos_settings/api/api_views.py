from django.conf import settings
from django.db.models import Count
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from conventions.models import ConventionStatut
from siap.siap_authentication import SIAPJWTAuthentication, SIAPSimpleJWTAuthentication


class ApilosConfiguration(APIView):
    """
    return the main configutations of the application
    """

    authentication_classes = [SIAPSimpleJWTAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    renderer_classes = [JSONRenderer]

    @extend_schema(
        tags=["config-resource"],
        responses={
            200: inline_serializer(
                name="APiLosConfiguration",
                fields={
                    "racine_url_acces_web": serializers.CharField(
                        max_length=2000,
                        help_text="Racine de l'URL d'accès web à l'application avec son protocole",
                    ),
                    "url_acces_api_cloture_operation": serializers.CharField(
                        max_length=2000,
                        help_text=(
                            "Route API a appeler lors de la cloture de l'opération"
                            " en GET pour vérifier qu'il est possible de cloturer"
                            " en POST pour alerter de la cloture"
                        ),
                    ),
                    "url_acces_api_annulation_operation": serializers.CharField(
                        max_length=2000,
                        help_text=(
                            "Route API a appeler en POST lors de l'annulation de"
                            " l'opération"
                        ),
                    ),
                    "url_acces_api_conventions_operation": serializers.CharField(
                        max_length=2000,
                        help_text=(
                            "Route API permettant de récupérer les conventions"
                            " associées à une opération"
                        ),
                    ),
                    "url_acces_web_operation": serializers.CharField(
                        max_length=2000,
                        help_text=(
                            "URL d'accès web à l'application sur la page d'une opération"
                            + " (en relatif)"
                        ),
                    ),
                    "url_acces_web_recherche": serializers.CharField(
                        max_length=2000,
                        help_text=(
                            "URL d'accès web à la page de recherche des conventions"
                            + " (en relatif)"
                        ),
                    ),
                    "url_acces_api_kpi": serializers.CharField(
                        max_length=2000,
                        help_text=(
                            "URL d'accès API aux indicateurs de conventionnement à afficher"
                            + " sur le tableau de bord (en relatif)"
                        ),
                    ),
                    "version": serializers.CharField(
                        max_length=20,
                        help_text=(
                            "version API x.y, La version majeure sera indentée seulement en cas"
                            + " de non compatibilité"
                        ),
                    ),
                },
            ),
            400: OpenApiResponse(description="Bad request (something invalid)"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not Found"),
        },
        examples=[
            OpenApiExample(
                "Configuration",
                summary="Example of returned configuration",
                description="Example of returned configuration when /config url is called",
                value={
                    "racine_url_acces_web": "https://apilos.beta.gouv.fr",
                    "url_acces_api_cloture_operation": (
                        "/api-siap/v0/close_operation/{NUMERO_OPERATION_SIAP}/"
                    ),
                    "url_acces_api_annulation_operation": (
                        "/api-siap/v0/cancel_operation/{NUMERO_OPERATION_SIAP}/"
                    ),
                    "url_acces_api_conventions_operation": (
                        "/api-siap/v0/operation/{NUMERO_OPERATION_SIAP}"
                    ),
                    "url_acces_api_kpi": "/api-siap/v0/convention_kpi/",
                    "url_acces_web_operation": "/operations/{NUMERO_OPERATION_SIAP}/",
                    "url_acces_web_recherche": "/conventions/",
                    "version": "0.1",
                },
                request_only=False,  # signal that example only applies to requests
                response_only=True,  # signal that example only applies to responses
            ),
        ],
    )
    def get(self, request):
        """
        Return main settings of the application.
        """
        if request.is_secure():
            protocol = "https://"
        else:
            protocol = "http://"
        version = ".".join(settings.SPECTACULAR_SETTINGS["VERSION"].split(".")[:-1])
        return Response(
            {
                "racine_url_acces_web": protocol + request.get_host(),
                "url_acces_api_cloture_operation": (
                    "/api-siap/v0/close_operation/{NUMERO_OPERATION_SIAP}/"
                ),
                "url_acces_api_annulation_operation": (
                    "/api-siap/v0/cancel_operation/{NUMERO_OPERATION_SIAP}/"
                ),
                "url_acces_api_conventions_operation": (
                    "/api-siap/v0/operation/{NUMERO_OPERATION_SIAP}"
                ),
                "url_acces_api_kpi": "/api-siap/v0/convention_kpi/",
                "url_acces_web_operation": "/operations/{NUMERO_OPERATION_SIAP}",
                "url_acces_web_recherche": "/conventions",
                "version": version,
            }
        )


class ConvKPI:
    def __init__(self, indicateur_redirection_url, indicateur_valeur, indicateur_label):
        self.indicateur_redirection_url = indicateur_redirection_url
        self.indicateur_valeur = indicateur_valeur
        self.indicateur_label = indicateur_label


class ConventionKPISerializer(serializers.Serializer):
    indicateur_redirection_url = serializers.CharField(max_length=200)
    indicateur_valeur = serializers.IntegerField()
    indicateur_label = serializers.CharField(max_length=100)


class ConventionKPI(APIView):
    """
    return the main configutations of the application
    """

    authentication_classes = [SIAPJWTAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["statistics"],
        responses={
            200: ConventionKPISerializer(many=True),
            400: OpenApiResponse(description="Bad request (something invalid)"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not Found"),
        },
    )
    def get(self, request):
        """
        Return main settings of the application.
        """
        query_by_statuses = (
            request.user.conventions()
            .filter(parent_id__isnull=True)
            .values("statut")
            .annotate(total=Count("statut"))
        )

        nb_conventions_by_status = {
            convention_statut.label: 0 for convention_statut in ConventionStatut
        } | {query["statut"]: query["total"] for query in query_by_statuses}
        list_conv_kpi = []

        if request.user.is_administration():
            # As an administrator, we want to see the number of conventions that are in status:
            #   * en-cours
            #   * SIGNEE
            list_conv_kpi = [
                ConvKPI(
                    "/conventions/en-cours",
                    nb_conventions_by_status[ConventionStatut.PROJET.label]
                    + nb_conventions_by_status[ConventionStatut.INSTRUCTION.label]
                    + nb_conventions_by_status[ConventionStatut.CORRECTION.label]
                    + nb_conventions_by_status[ConventionStatut.A_SIGNER.label],
                    "en cours",
                ),
                ConvKPI(
                    "/conventions/actives",
                    nb_conventions_by_status[ConventionStatut.SIGNEE.label],
                    "finalisées",
                ),
            ]
        elif request.user.is_instructeur():
            # As an instructeur, we want to see the number of conventions that are in status:
            #   * INSTRUCTION
            #   * A_SIGNER
            #   * SIGNEE
            list_conv_kpi = [
                ConvKPI(
                    "/conventions/en-cours?cstatut=2.+Instruction+requise",
                    nb_conventions_by_status[ConventionStatut.INSTRUCTION.label],
                    "en instruction",
                ),
                ConvKPI(
                    "/conventions/en-cours?cstatut=4.+A+signer",
                    nb_conventions_by_status[ConventionStatut.A_SIGNER.label],
                    "à signer",
                ),
                ConvKPI(
                    "/conventions/actives",
                    nb_conventions_by_status[ConventionStatut.SIGNEE.label],
                    "finalisées",
                ),
            ]
        elif request.user.is_bailleur():
            # As a bailleur, we want to see the number of conventions that are in status:
            #   * PROJET
            #   * CORRRECTION
            #   * A_SIGNER
            list_conv_kpi = [
                ConvKPI(
                    "/conventions/en-cours?cstatut=1.+Projet",
                    nb_conventions_by_status[ConventionStatut.PROJET.label],
                    "en projet",
                ),
                ConvKPI(
                    "/conventions/en-cours?cstatut=3.+Corrections+requises",
                    nb_conventions_by_status[ConventionStatut.CORRECTION.label],
                    "en correction requise",
                ),
                ConvKPI(
                    "/conventions/actives",
                    nb_conventions_by_status[ConventionStatut.A_SIGNER.label],
                    "à signer",
                ),
            ]
        return Response(ConventionKPISerializer(list_conv_kpi, many=True).data)
