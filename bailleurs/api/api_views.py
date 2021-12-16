from django.http import Http404
from rest_framework.response import Response
from rest_framework import status, mixins, generics
from bailleurs.models import Bailleur
from bailleurs.api.serializers import BailleurSerializer


class BailleurList(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    """
    List all bailleurs, or create a new bailleur.
    """

    serializer_class = BailleurSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        return self.request.user.bailleurs()

    def get(self, request):  # , format=None):
        return self.list(request)  # , *args, **kwargs)

    def post(self, request):  # , format=None):
        serializer = BailleurSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BailleurDetail(generics.GenericAPIView):
    """
    Retrieve, update or delete a bailleur instance.
    """

    serializer_class = BailleurSerializer

    # pylint: disable=R0201 no-self-use
    def get_object_by_uuid(self, uuid):
        try:
            return Bailleur.objects.get(uuid=uuid)
        except Bailleur.DoesNotExist as does_not_exist:
            raise Http404 from does_not_exist

    def get(self, request, uuid):  # , format=None):
        bailleur = self.get_object_by_uuid(uuid)
        serializer = BailleurSerializer(bailleur)
        return Response(serializer.data)

    def put(self, request, uuid):  # , format=None):
        bailleur = self.get_object_by_uuid(uuid)
        serializer = BailleurSerializer(bailleur, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uuid):  # , format=None):
        bailleur = self.get_object_by_uuid(uuid)
        bailleur.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
