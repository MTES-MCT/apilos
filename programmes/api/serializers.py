from rest_framework import serializers
from programmes.models import Programme


class ProgrammeSerializer(serializers.HyperlinkedModelSerializer):
    #    uuid = serializers.CharField(read_only=True)
    #    nom = serializers.CharField(max_length=255)
    # bailleur = models.ForeignKey(
    #     "bailleurs.Bailleur", on_delete=models.CASCADE, null=False
    # )
    # administration = models.ForeignKey(
    #     "instructeurs.Administration", on_delete=models.SET_NULL, null=True
    # )
    #    code_postal = serializers.CharField(max_length=10, null=True)
    # ville = models.CharField(max_length=255, null=True)
    # adresse = models.CharField(max_length=255, null=True)
    # numero_galion = models.CharField(max_length=255, null=True)
    # annee_gestion_programmation = models.IntegerField(null=True)
    # zone_123 = models.IntegerField(null=True)
    # zone_abc = models.CharField(max_length=255, null=True)
    # surface_utile_totale = models.DecimalField(
    #     max_digits=8, decimal_places=2, null=True
    # )
    # type_habitat = models.CharField(
    #     max_length=25,
    #     choices=TypeHabitat.choices,
    #     default=TypeHabitat.INDIVIDUEL,
    # )
    # type_operation = models.CharField(
    #     max_length=25,
    #     choices=TypeOperation.choices,
    #     default=TypeOperation.NEUF,
    # )
    # anru = models.BooleanField(default=False)
    # nb_locaux_commerciaux = models.IntegerField(null=True)
    # nb_bureaux = models.IntegerField(null=True)
    # autres_locaux_hors_convention = models.TextField(null=True)
    # vendeur = models.TextField(null=True)
    # acquereur = models.TextField(null=True)
    # date_acte_notarie = models.DateField(null=True)
    # reference_notaire = models.TextField(null=True)
    # reference_publication_acte = models.TextField(null=True)
    # acte_de_propriete = models.TextField(null=True)
    # acte_notarial = models.TextField(null=True)
    # reference_cadastrale = models.TextField(null=True)
    # edd_volumetrique = models.TextField(max_length=5000, null=True)
    # mention_publication_edd_volumetrique = models.TextField(max_length=1000, null=True)
    # edd_classique = models.TextField(max_length=5000, null=True)
    # mention_publication_edd_classique = models.TextField(max_length=1000, null=True)
    # permis_construire = models.CharField(max_length=255, null=True)
    # date_achevement_previsible = models.DateField(null=True)
    # date_achat = models.DateField(null=True)
    # date_achevement = models.DateField(null=True)
    # cree_le = models.DateTimeField(auto_now_add=True)
    # mis_a_jour_le = models.DateTimeField(auto_now=True)

    class Meta:
        model = Programme
        fields = ["uuid", "nom", "type_habitat", "type_operation"]

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Programme.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Programme` instance, given the validated data.
        """
        instance.nom = validated_data.get("nom", instance.title)
        instance.save()
        return instance
