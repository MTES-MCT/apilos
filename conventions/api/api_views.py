from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import mixins, generics
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

# from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.csrf_exempt_session_authentication import CsrfExemptSessionAuthentication
from bailleurs.models import Bailleur
from conventions.models import Convention
from conventions.api.serializers import ConventionSerializer
from conventions.api.permissions import ConventionPermission


class ConventionList(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    """
    List all conventions, or create a new convention.
    """

    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, ConventionPermission]
    http_method_names = ["get", "head"]

    serializer_class = ConventionSerializer
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = [
    #     "bailleur",
    #     # "progamme__administration__uuid"
    # ]

    bailleur_uuid_param = openapi.Parameter(
        "bailleur_uuid",
        openapi.IN_QUERY,
        description="UUID du bailleur",
        required=False,
        type=openapi.TYPE_STRING,
    )

    # progamme__administration__uuid_param = openapi.Parameter(
    #     "progamme__administration__uuid",
    #     openapi.IN_QUERY,
    #     description="UUID d l'administration",
    #     required=False,
    #     type=openapi.TYPE_STRING,
    # )

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        convention_filter = {}
        if "bailleur_uuid" in self.request.query_params:
            bailleur = Bailleur.objects.get(
                uuid=self.request.query_params["bailleur_uuid"]
            )
            convention_filter["bailleur_id"] = bailleur.id
        return self.request.user.conventions().filter(**convention_filter)

    @swagger_auto_schema(
        manual_parameters=[
            bailleur_uuid_param,
            # progamme__administration__uuid_param,
        ]
    )
    def get(self, request):  # , format=None):
        return self.list(request)  # , *args, **kwargs)


class ConventionDetail(generics.GenericAPIView):
    """
    Retrieve, update or delete a convention instance.
    """

    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, ConventionPermission]
    http_method_names = ["get", "head"]

    serializer_class = ConventionSerializer

    # pylint: disable=W0221 arguments-differ
    def get_object(self, uuid):
        try:
            convention = Convention.objects.get(uuid=uuid)
            return convention
        except Convention.DoesNotExist as does_not_exist:
            raise Http404 from does_not_exist

    def get(self, request, uuid):  # , format=None):
        convention = self.get_object(uuid)
        if not ConventionPermission.has_object_permission(
            self, request, self, convention
        ):
            raise PermissionDenied
        serializer = ConventionSerializer(convention)
        return Response(serializer.data)
