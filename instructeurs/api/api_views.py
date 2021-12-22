from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status, mixins, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from api.csrf_exempt_session_authentication import CsrfExemptSessionAuthentication
from instructeurs.models import Administration
from instructeurs.api.serializers import AdministrationSerializer
from instructeurs.api.permissions import AdministrationPermission


class AdministrationList(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    """
    List all administrations, or create a new administration.
    """

    #    authentication_classes = [SessionAuthentication, BasicAuthentication]
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, AdministrationPermission]

    serializer_class = AdministrationSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        return self.request.user.administrations()

    def get(self, request):  # , format=None):
        return self.list(request)  # , *args, **kwargs)

    def post(self, request):  # , format=None):
        serializer = AdministrationSerializer(data=request.data, context=request)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdministrationDetail(generics.GenericAPIView):
    """
    Retrieve, update or delete a administration instance.
    """

    #    authentication_classes = [SessionAuthentication, BasicAuthentication]
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, AdministrationPermission]

    serializer_class = AdministrationSerializer

    # pylint: disable=W0221 arguments-differ
    def get_object(self, uuid):
        try:
            administration = Administration.objects.get(uuid=uuid)
            return administration
        except Administration.DoesNotExist as does_not_exist:
            raise Http404 from does_not_exist

    def get(self, request, uuid):  # , format=None):
        administration = self.get_object(uuid)
        if not AdministrationPermission.has_object_permission(
            self, request, self, administration
        ):
            raise PermissionDenied
        serializer = AdministrationSerializer(administration)
        return Response(serializer.data)

    def put(self, request, uuid):  # , format=None):
        administration = self.get_object(uuid)
        if not AdministrationPermission.has_object_permission(
            self, request, self, administration
        ):
            raise PermissionDenied
        serializer = AdministrationSerializer(
            administration, data=request.data, partial=True, context=request
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid):  # , format=None):
        administration = self.get_object(uuid)
        if not AdministrationPermission.has_object_permission(
            self, request, self, administration
        ):
            raise PermissionDenied
        administration.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
