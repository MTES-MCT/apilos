from django.http import Http404
from rest_framework import serializers

from bailleurs.models import Bailleur
from bailleurs.api.serializers import BailleurSerializer

from programmes.models import Programme


class ProgrammeSerializer(serializers.HyperlinkedModelSerializer):
    bailleur = BailleurSerializer(read_only=True)
    bailleur_uuid = serializers.CharField(write_only=True)

    class Meta:
        model = Programme
        fields = [
            "uuid",
            "nom",
            "bailleur",
            "bailleur_uuid",
            # "administration",
            "code_postal",
            "ville",
            "adresse",
            "numero_galion",
            "annee_gestion_programmation",
            "zone_123",
            "zone_abc",
            "surface_utile_totale",
            "type_habitat",
            "type_operation",
            "anru",
            "nb_locaux_commerciaux",
            "nb_bureaux",
            "autres_locaux_hors_convention",
            "date_acte_notarie",
            "mention_publication_edd_volumetrique",
            "mention_publication_edd_classique",
            "permis_construire",
            "date_achevement_previsible",
            "date_achat",
            "date_achevement",
        ]
        read_only_fields = (
            "vendeur",
            "acquereur",
            "reference_notaire",
            "reference_publication_acte",
            "acte_de_propriete",
            "acte_notarial",
            "reference_cadastrale",
            "edd_volumetrique",
            "edd_classique",
        )

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        bailleur_uuid = validated_data.pop("bailleur_uuid")
        try:
            bailleur = Bailleur.objects.get(uuid=bailleur_uuid)
        except Bailleur.DoesNotExist as does_not_exist:
            raise Http404("bailleur non trouvé") from does_not_exist
        return Programme.objects.create(**validated_data, bailleur=bailleur)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Programme` instance, given the validated data.
        """
        instance.nom = validated_data.get("nom", instance.nom)
        instance.zone_123 = validated_data.get("zone_123", instance.zone_123)
        instance.save()
        return instance
