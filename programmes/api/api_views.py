from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status, mixins, generics
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from programmes.models import Programme
from programmes.api.serializers import ProgrammeSerializer
from programmes.api.permissions import ProgrammePermission


class ProgrammeList(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    """
    List all programmes, or create a new programme.
    """

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, ProgrammePermission]

    serializer_class = ProgrammeSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        return self.request.user.programmes()

    def get(self, request):  # , format=None):
        return self.list(request)  # , *args, **kwargs)

    def post(self, request):  # , format=None):
        serializer = ProgrammeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProgrammeDetail(generics.GenericAPIView):
    """
    Retrieve, update or delete a programme instance.
    """

    authentication_classes = [SessionAuthentication, BasicAuthentication]
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
        serializer = ProgrammeSerializer(programme, data=request.data, partial=True)
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
