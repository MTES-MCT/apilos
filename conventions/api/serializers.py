from rest_framework import serializers

from bailleurs.api.serializers import BailleurSerializer
from programmes.api.serializers import ProgrammeSerializer, LotSerializer

from conventions.models import Convention


class ConventionSerializer(serializers.HyperlinkedModelSerializer):
    bailleur = BailleurSerializer(read_only=True)
    programme = ProgrammeSerializer(read_only=True)
    lot = LotSerializer(read_only=True)

    class Meta:
        model = Convention
        fields = (
            "uuid",
            "numero",
            "bailleur",
            "programme",
            "lot",
        )
