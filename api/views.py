from rest_framework import viewsets, permissions
from users.models import User
from programmes.models import Programme, Lot, Logement, LogementEDD, Annexe
from api.serializers import (
    UserSerializer,
    ProgrammeSerializer,
    LotSerializer,
    LogementSerializer,
    LogementEDDSerializer,
    AnnexeSerializer,
)


class UserViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProgrammeViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """
    API endpoint that allows Programmes to be viewed or edited.
    """

    queryset = Programme.objects.all()
    serializer_class = ProgrammeSerializer
    permission_classes = [permissions.IsAuthenticated]


class LotViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """
    API endpoint that allows Lots to be viewed or edited.
    """

    queryset = Lot.objects.all()
    serializer_class = LotSerializer
    permission_classes = [permissions.IsAuthenticated]


class LogementViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """
    API endpoint that allows Logements to be viewed or edited.
    """

    queryset = Logement.objects.all()
    serializer_class = LogementSerializer
    permission_classes = [permissions.IsAuthenticated]


class LogementEDDViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """
    API endpoint that allows LogementEDDs to be viewed or edited.
    """

    queryset = LogementEDD.objects.all()
    serializer_class = LogementEDDSerializer
    permission_classes = [permissions.IsAuthenticated]


class AnnexeViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """
    API endpoint that allows Annexes to be viewed or edited.
    """

    queryset = Annexe.objects.all()
    serializer_class = AnnexeSerializer
    permission_classes = [permissions.IsAuthenticated]
