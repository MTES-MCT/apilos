from rest_framework import serializers
from bailleurs.models import Bailleur


class BailleurSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bailleur
        fields = [
            "uuid",
            "nom",
            "siret",
            "adresse",
            "code_postal",
            "ville",
            "capital_social",
            "signataire_nom",
            "signataire_fonction",
            "signataire_date_deliberation",
            "type_bailleur",
            "cree_le",
            "mis_a_jour_le",
        ]
        ref_name = "BailleurEmbeddedSchema"
