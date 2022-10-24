from django.http import Http404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
)

from siap.siap_authentication import SIAPJWTAuthentication
from programmes.services import get_or_create_conventions_from_operation_number
from programmes.models import Programme
from programmes.api.operation_serializers import OperationSerializer as MySerializer


class OperationDetails(generics.GenericAPIView):
    """
    Retrieve, update or delete a programme instance.
    """

    authentication_classes = [SIAPJWTAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    serializer_class = MySerializer

    # pylint: disable=W0221 arguments-differ
    def get_object(self, numero_galion):
        try:
            programme = Programme.objects.get(numero_galion=numero_galion)
            return programme
        except Programme.DoesNotExist as does_not_exist:
            raise Http404 from does_not_exist

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
        programme = self.get_object(numero_galion)
        serializer = MySerializer(programme)
        return Response(serializer.data)

    def post(self, request, numero_galion):
        (programme, _, _) = get_or_create_conventions_from_operation_number(
            request, numero_galion
        )
        serializer = MySerializer(programme)
        return Response(serializer.data)
