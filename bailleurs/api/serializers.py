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
            "cree_le",
            "mis_a_jour_le",
        ]

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Bailleur.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Bailleur` instance, given the validated data.
        """
        instance.nom = validated_data.get("nom", instance.nom)
        instance.save()
        return instance
