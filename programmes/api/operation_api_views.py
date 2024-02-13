from django.http import Http404
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from conventions.models.choices import ConventionStatut
from programmes.api.operation_serializers import ClosingOperationSerializer
from programmes.api.operation_serializers import OperationSerializer as MySerializer
from programmes.models import Programme
from programmes.services import get_or_create_conventions_from_operation_number
from siap.siap_authentication import SIAPJWTAuthentication


class OperationApiViewBase(generics.GenericAPIView):
    authentication_classes = [SIAPJWTAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_last_relevant_programme(self, numero_galion):
        try:
            # dernière version
            programme = (
                Programme.objects.filter(numero_galion=numero_galion)
                .order_by("-cree_le")
                .first()
            )
            return programme
        except Programme.DoesNotExist as does_not_exist:
            raise Http404 from does_not_exist


class OperationDetails(OperationApiViewBase):
    """
    Retrieve, update or delete a programme instance.
    """

    @extend_schema(
        tags=["operation"],
        responses={
            200: MySerializer,
            400: OpenApiResponse(description="Bad request (something invalid)"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not Found"),
        },
        description="Return Operations and all its conventions",
    )
    def get(self, request, numero_galion):
        programme = self.get_last_relevant_programme(numero_galion)
        serializer = MySerializer(programme)
        return Response(serializer.data)

    @extend_schema(
        tags=["operation"],
        responses={
            200: MySerializer,
            400: OpenApiResponse(description="Bad request (something invalid)"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not Found"),
        },
        description="Create all convention objects linked to an operation and retour"
        + " all those created element",
    )
    def post(self, request, numero_galion):
        (programme, _, _) = get_or_create_conventions_from_operation_number(
            request, numero_galion
        )
        serializer = MySerializer(programme)
        return Response(serializer.data)


# empty class to prepare routes for SIAP:
# * OperationClosed.get -> get the status of the last version of the convention
# * OperationClosed.post -> create avenant if needed after operation is closed
class OperationClosed(OperationApiViewBase):
    @extend_schema(
        tags=["operation"],
        responses={
            200: ClosingOperationSerializer,
            400: OpenApiResponse(description="Bad request (something invalid)"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not Found"),
        },
        description=(
            "Return Operation and all its conventions with a summary of"
            + " last data validated by conventions and its avenant (to do)"
        ),
    )
    def get(self, request, numero_galion):
        programme = self.get_last_relevant_programme(numero_galion)
        serializer = ClosingOperationSerializer(programme)
        return Response(serializer.data)

    @extend_schema(
        tags=["operation"],
        responses={
            200: ClosingOperationSerializer,
            400: OpenApiResponse(description="Bad request (something invalid)"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not Found"),
        },
        description=(
            "Get last data from Operations and create Avenants if it is needed (to do)"
        ),
    )
    def post(self, request, numero_galion):
        return self.get(request, numero_galion)


# empty class to prepare routes for SIAP:
# * OperationClosed.get -> get the status of the last version of the convention
# * OperationClosed.post -> create avenant if needed after operation is closed
class OperationCanceled(OperationApiViewBase):
    @extend_schema(
        tags=["operation"],
        responses={
            200: OpenApiResponse(description="JSON with status and message"),
            400: OpenApiResponse(description="Bad request (something invalid)"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
            404: OpenApiResponse(description="Not Found"),
        },
        description=(
            "Cancel opération's conventions, return a status and a message"
            "if the cancelation is not possible."
        ),
        examples=[
            OpenApiExample(
                "Cancelation with success",
                summary="Example when cancelation is possible",
                description=(
                    "Example when cancelation is possible,"
                    " operation's convention are canceled"
                ),
                value={
                    "status": "SUCCESS",
                },
                request_only=False,  # signal that example only applies to requests
                response_only=True,  # signal that example only applies to responses
            ),
            OpenApiExample(
                "Cancelation failed",
                summary="Example when cancelation is not possible",
                description=(
                    "Example when cancelation is not possible,"
                    " operation's convention are not canceled"
                ),
                value={
                    "status": "ERROR",
                    "message": (
                        "Au moins une des conventions de l'opération ne peut être"
                        " supprimée car elle est active. Vous devez dénoncer ou"
                        " résilier toutes les conventions de l'opération avant de"
                        " demander sa suppression."
                    ),
                },
                request_only=False,  # signal that example only applies to requests
                response_only=True,  # signal that example only applies to responses
            ),
        ],
    )
    def post(self, request, numero_galion):
        programmes = Programme.objects.filter(
            numero_galion=numero_galion, parent_id=None
        )

        if any(
            convention.statut == ConventionStatut.SIGNEE.label
            for programme in programmes
            for convention in programme.conventions.all()
        ):
            return Response(
                {
                    "status": "ERROR",
                    "message": (
                        "Au moins une des conventions de l'opération ne peut être"
                        " supprimée car elle est active. Vous devez dénoncer ou"
                        " résilier toutes les conventions de l'opération avant de"
                        " demander sa suppression."
                    ),
                },
            )

        for programme in programmes:
            for convention in programme.conventions.all():
                convention.cancel()

        return Response({"status": "SUCCESS"})
