from rest_framework import serializers

from instructeurs.models import Administration


class AdministrationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Administration
        fields = [
            "uuid",
            "nom",
            "code",
            "ville_signature",
        ]

    def create(self, validated_data):
        """
        Create and return a new `Administration` instance, given the validated data.
        """
        return Administration.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Administration` instance, given the validated data.
        """
        for field in [
            "nom",
            "code",
            "ville_signature",
        ]:
            setattr(
                instance, field, validated_data.get(field, getattr(instance, field))
            )

        instance.save()
        return instance
