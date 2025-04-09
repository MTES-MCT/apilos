from rest_framework import serializers

from bailleurs.models import Bailleur
from conventions.models import Convention, Pret
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


class PretSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Pret
        fields = (
            "preteur",
            "autre",
            "date_octroi",
            "numero",
            "duree",
            "montant",
        )
        ref_name = "Pret"


class LotSerializer(serializers.HyperlinkedModelSerializer):
    logements = LogementSerializer(many=True)
    type_stationnements = TypeStationnementSerializer(many=True)
    prets = PretSerializer(many=True)

    class Meta:
        model = Lot
        fields = (
            "nb_logements",
            "financement",
            "type_habitat",
            "prets",
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
            "numero_operation",
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
    lots = LotSerializer(many=True)
    operation_version = OperationVersionSerializer(source="programme", read_only=True)

    class Meta:
        model = Convention
        fields = (
            "date_fin_conventionnement",
            "fond_propre",
            "lots",
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
            "numero_operation",
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


class OperationInfoSIAPSerializer(serializers.ModelSerializer):
    bailleur = BailleurSerializer(read_only=True)
    administration = AdministrationSerializer(read_only=True)

    class Meta:
        model = Programme
        fields = (
            "nom",
            "bailleur",
            "administration",
            "code_postal",
            "ville",
            "adresse",
            "numero_operation",
            "nature_logement",
            "zone_123",
            "zone_abc",
            "type_operation",
            "anru",
            "date_achevement_previsible",
            "date_achat",
            "date_achevement",
        )
        ref_name = "OperationInfoSIAP"


class ConventionInfoSIAPSerializer(serializers.ModelSerializer):
    lots = LotSerializer(many=True)
    operation = OperationInfoSIAPSerializer(source="programme", read_only=True)
    numero_avenant = serializers.SerializerMethodField()
    numero_convention = serializers.SerializerMethodField()
    convention_date_signature = serializers.SerializerMethodField()
    convention_parent_uuid = serializers.SerializerMethodField()
    depuis_ecoloweb = serializers.SerializerMethodField()
    avenant_types = serializers.SerializerMethodField()

    def get_avenant_types(self, obj):
        return [avenant_type.nom for avenant_type in obj.avenant_types.all()]

    def get_numero_convention(self, obj):
        if obj.parent:
            return obj.parent.numero
        return obj.numero

    def get_convention_parent_uuid(self, obj):
        if obj.parent:
            return str(obj.parent.uuid)
        return None

    def get_depuis_ecoloweb(self, obj):
        return bool(obj.ecolo_reference)

    def get_numero_avenant(self, obj):
        if obj.parent:
            return obj.numero
        return None

    def get_convention_date_signature(self, obj):
        if obj.parent:
            return obj.parent.televersement_convention_signee_le
        return obj.televersement_convention_signee_le

    # ajout de la date de signature de la convention mère
    # vérifier si le numéro de la convention est le numéro de la convention mère
    class Meta:
        model = Convention
        fields = (
            "uuid",
            "convention_parent_uuid",
            "numero_convention",
            "numero_avenant",
            "avenant_types",
            "depuis_ecoloweb",
            "date_fin_conventionnement",
            "convention_date_signature",
            "date_denonciation",
            "date_resiliation",
            "fond_propre",
            "gestionnaire",
            "statut",
            "operation",
            "lots",
        )
        ref_name = "ConventionInfoSIAP"
