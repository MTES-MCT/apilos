from django.http import Http404
from rest_framework.response import Response
from rest_framework import status, mixins, generics
from programmes.models import Programme
from programmes.api.serializers import ProgrammeSerializer


class ProgrammeList(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    """
    List all programmes, or create a new programme.
    """

    serializer_class = ProgrammeSerializer

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

    serializer_class = ProgrammeSerializer

    # pylint: disable=R0201 no-self-use
    def get_object_by_uuid(self, uuid):
        try:
            return Programme.objects.get(uuid=uuid)
        except Programme.DoesNotExist as does_not_exist:
            raise Http404 from does_not_exist

    def get(self, request, uuid):  # , format=None):
        programme = self.get_object_by_uuid(uuid)
        serializer = ProgrammeSerializer(programme)
        return Response(serializer.data)

    def put(self, request, uuid):  # , format=None):
        programme = self.get_object_by_uuid(uuid)
        serializer = ProgrammeSerializer(programme, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid):  # , format=None):
        programme = self.get_object_by_uuid(uuid)
        programme.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
