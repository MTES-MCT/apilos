from rest_framework import serializers

from bailleurs.models import Bailleur
from conventions.models import Convention
from instructeurs.models import Administration
from programmes.models import Annexe, Logement, Lot, Programme, TypeStationnement


class BailleurSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bailleur
        fields = (
            "nom",
            "siren",
            "siret",
            "adresse",
            "code_postal",
            "ville",
            "capital_social",
            "sous_nature_bailleur",
        )
        ref_name = "Bailleur"


class AdministrationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Administration
        fields = (
            "nom",
            "code",
            "ville_signature",
        )
        ref_name = "Administration"


class AnnexeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Annexe
        fields = (
            "typologie",
            "surface_hors_surface_retenue",
            "loyer_par_metre_carre",
            "loyer",
        )
        ref_name = "Annexe"


class LogementSerializer(serializers.HyperlinkedModelSerializer):
    annexes = AnnexeSerializer(many=True)

    class Meta:
        model = Logement
        fields = (
            "designation",
            "typologie",
            "surface_habitable",
            "surface_annexes",
            "surface_annexes_retenue",
            "surface_utile",
            "loyer_par_metre_carre",
            "coeficient",
            "loyer",
            "annexes",
        )
        ref_name = "Logement"


class TypeStationnementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TypeStationnement
        fields = (
            "typologie",
            "nb_stationnements",
            "loyer",
        )
        ref_name = "TypeStationnement"


class LotSerializer(serializers.HyperlinkedModelSerializer):
    logements = LogementSerializer(many=True)
    type_stationnements = TypeStationnementSerializer(many=True)

    class Meta:
        model = Lot
        fields = (
            "nb_logements",
            "financement",
            "type_habitat",
            "logements",
            "type_stationnements",
        )
        ref_name = "Lot"


class OperationVersionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Programme
        fields = (
            "nom",
            "code_postal",
            "ville",
            "adresse",
            "numero_galion",
            "zone_123",
            "zone_abc",
            "type_operation",
            "anru",
            "date_achevement_previsible",
            "date_achat",
            "date_achevement",
        )
        ref_name = "Operation"


class ConventionSerializer(serializers.HyperlinkedModelSerializer):
    lot = LotSerializer(read_only=True)
    operation_version = OperationVersionSerializer(source="programme", read_only=True)

    class Meta:
        model = Convention
        fields = (
            "date_fin_conventionnement",
            "financement",
            "fond_propre",
            "lot",
            "operation_version",
            "numero",
            "statut",
        )
        ref_name = "Convention"


class OperationSerializer(serializers.HyperlinkedModelSerializer):
    bailleur = BailleurSerializer(read_only=True)
    administration = AdministrationSerializer(read_only=True)
    conventions = ConventionSerializer(source="all_conventions", many=True)

    # Deprecated fields to check with SIAP Sully team:
    #   nom, code_postal, ville, adresse, zone_123, zone_abc,
    #   type_operation, anru, date_achevement_previsible, date_achat, date_achevement

    class Meta:
        model = Programme
        fields = (
            "nom",
            "bailleur",
            "administration",
            "conventions",
            "code_postal",
            "ville",
            "adresse",
            "numero_galion",
            "zone_123",
            "zone_abc",
            "type_operation",
            "anru",
            "date_achevement_previsible",
            "date_achat",
            "date_achevement",
        )
        ref_name = "Operation"


class ClosingOperationSerializer(OperationSerializer):
    last_conventions_state = ConventionSerializer(many=True)

    class Meta:
        model = OperationSerializer.Meta.model
        fields = OperationSerializer.Meta.fields + (
            "all_conventions_are_signed",
            "last_conventions_state",
        )
        ref_name = "ClosingOperation"
