from rest_framework import serializers
from users.models import User
from programmes.models import Programme, Lot, Logement, LogementEDD, Annexe


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class ProgrammeSerializer(serializers.HyperlinkedModelSerializer):
    default_fields = ("uuid",)

    class Meta:
        model = Programme
        fields = ["uuid", "nom", "type_habitat", "type_operation"]


class LotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Lot
        fields = ["uuid", "financement", "nb_logements"]


class LogementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Logement
        fields = ["uuid", "designation", "typologie", "loyer"]


class LogementEDDSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LogementEDD
        fields = ["uuid", "designation", "typologie"]


class AnnexeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Annexe
        fields = ["uuid", "typologie"]
