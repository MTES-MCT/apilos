from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status, mixins, generics
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.csrf_exempt_session_authentication import CsrfExemptSessionAuthentication
from programmes.models import Programme, Lot
from programmes.api.serializers import ProgrammeSerializer, LotSerializer
from programmes.api.permissions import ProgrammePermission, LotPermission


class ProgrammeList(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    """
    List all programmes, or create a new programme.
    """

    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, ProgrammePermission]

    serializer_class = ProgrammeSerializer

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["nom", "code_postal", "ville"]
    filterset_fields = ["nom", "code_postal", "ville", "numero_galion"]
    nom_param = openapi.Parameter(
        "nom",
        openapi.IN_QUERY,
        description="Nom du programme",
        required=False,
        type=openapi.TYPE_STRING,
    )
    code_postal_param = openapi.Parameter(
        "code_postal",
        openapi.IN_QUERY,
        description="Code postal du programme",
        required=False,
        type=openapi.TYPE_STRING,
    )
    ville_param = openapi.Parameter(
        "ville",
        openapi.IN_QUERY,
        description="Ville du programme",
        required=False,
        type=openapi.TYPE_STRING,
    )
    numero_galion_param = openapi.Parameter(
        "numero_galion",
        openapi.IN_QUERY,
        description="Numéro galion du programme",
        required=False,
        type=openapi.TYPE_STRING,
    )

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        return self.request.user.programmes()

    @swagger_auto_schema(
        manual_parameters=[
            nom_param,
            code_postal_param,
            ville_param,
            numero_galion_param,
        ]
    )
    def get(self, request):  # , format=None):
        return self.list(request)  # , *args, **kwargs)

    def post(self, request):  # , format=None):
        serializer = ProgrammeSerializer(data=request.data, context=request)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProgrammeDetail(generics.GenericAPIView):
    """
    Retrieve, update or delete a programme instance.
    """

    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, ProgrammePermission]

    serializer_class = ProgrammeSerializer

    # pylint: disable=W0221 arguments-differ
    def get_object(self, uuid):
        try:
            programme = Programme.objects.get(uuid=uuid)
            return programme
        except Programme.DoesNotExist as does_not_exist:
            raise Http404 from does_not_exist

    def get(self, request, uuid):  # , format=None):
        programme = self.get_object(uuid)
        if not ProgrammePermission.has_object_permission(
            self, request, self, programme
        ):
            raise PermissionDenied
        serializer = ProgrammeSerializer(programme)
        return Response(serializer.data)

    def put(self, request, uuid):  # , format=None):
        programme = self.get_object(uuid)
        if not ProgrammePermission.has_object_permission(
            self, request, self, programme
        ):
            raise PermissionDenied
        serializer = ProgrammeSerializer(
            programme, data=request.data, partial=True, context=request
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid):  # , format=None):
        programme = self.get_object(uuid)
        if not ProgrammePermission.has_object_permission(
            self, request, self, programme
        ):
            raise PermissionDenied
        programme.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LotList(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """
    List all lots, or create a new lot.
    """

    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, LotPermission]

    serializer_class = LotSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        return self.request.user.lots()

    def get(self, request):  # , format=None):
        return self.list(request)  # , *args, **kwargs)

    def post(self, request):  # , format=None):
        serializer = LotSerializer(data=request.data, context=request)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LotDetail(generics.GenericAPIView):
    """
    Retrieve, update or delete a lot instance.
    """

    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, LotPermission]

    serializer_class = LotSerializer

    # pylint: disable=W0221 arguments-differ
    def get_object(self, uuid):
        try:
            lot = Lot.objects.get(uuid=uuid)
            return lot
        except Lot.DoesNotExist as does_not_exist:
            raise Http404 from does_not_exist

    def get(self, request, uuid):  # , format=None):
        lot = self.get_object(uuid)
        if not LotPermission.has_object_permission(self, request, self, lot):
            raise PermissionDenied
        serializer = LotSerializer(lot)
        return Response(serializer.data)

    def put(self, request, uuid):  # , format=None):
        lot = self.get_object(uuid)
        if not LotPermission.has_object_permission(self, request, self, lot):
            raise PermissionDenied
        serializer = LotSerializer(
            lot, data=request.data, partial=True, context=request
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid):  # , format=None):
        lot = self.get_object(uuid)
        if not LotPermission.has_object_permission(self, request, self, lot):
            raise PermissionDenied
        lot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
