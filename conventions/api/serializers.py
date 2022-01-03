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
            "bailleur",
            "cree_le",
            "date_fin_conventionnement",
            "financement",
            "fond_propre",
            "lot",
            "mis_a_jour_le",
            "numero",
            "premiere_soumission_le",
            "programme",
            "soumis_le",
            "statut",
            "uuid",
            "valide_le",
        )
