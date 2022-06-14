from rest_framework import serializers

from programmes.models import Programme, Lot
from bailleurs.models import Bailleur
from instructeurs.models import Administration
from conventions.models import Convention


class BailleurSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bailleur
        fields = (
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
        )
        ref_name = "Bailleur"


class AdministrationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Administration
        fields = (
            "uuid",
            "nom",
            "code",
            "ville_signature",
        )
        ref_name = "Administration"


class LotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Lot
        fields = (
            "uuid",
            "nb_logements",
            "financement",
            "type_habitat",
            "edd_volumetrique",
            "edd_classique",
        )
        ref_name = "Lot"


class ConventionSerializer(serializers.HyperlinkedModelSerializer):
    lot = LotSerializer(read_only=True)

    class Meta:
        model = Convention
        fields = (
            "cree_le",
            "date_fin_conventionnement",
            "financement",
            "fond_propre",
            "lot",
            "mis_a_jour_le",
            "numero",
            "premiere_soumission_le",
            "soumis_le",
            "statut",
            "uuid",
            "valide_le",
        )
        ref_name = "Convention"


class OperationSerializer(serializers.HyperlinkedModelSerializer):
    bailleur = BailleurSerializer(read_only=True)
    administration = AdministrationSerializer(read_only=True)
    conventions = ConventionSerializer(many=True)

    class Meta:
        model = Programme
        fields = (
            "uuid",
            "nom",
            "bailleur",
            "administration",
            "conventions",
            "code_postal",
            "ville",
            "adresse",
            "numero_galion",
            "annee_gestion_programmation",
            "zone_123_bis",
            "zone_abc_bis",
            "surface_utile_totale",
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
            "vendeur",
            "acquereur",
            "reference_notaire",
            "reference_publication_acte",
            "acte_de_propriete",
            "certificat_adressage",
            "effet_relatif",
            "reference_cadastrale",
            "edd_volumetrique",
            "edd_classique",
        )
        ref_name = "Operation"
