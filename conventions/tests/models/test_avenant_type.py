from django.test import TestCase
from conventions.models.avenant_type import AvenantType
from conventions.models import Convention
from conventions.models.avenant_type import AVENANT_TYPE_FIELDS_MAPPING
from programmes.models import Lot, Programme


class AvenantTypeModelsTest(TestCase):
    def test_array_fields_is_empty_if_key_is_unknown(self):
        assert len(AvenantType(nom="bailleur").fields) > 0
        assert len(AvenantType(nom="unknown").fields) == 0

    def test_mapping_fields_exist(self):
        mapping_values = []
        for item in AVENANT_TYPE_FIELDS_MAPPING.values():
            mapping_values.extend(item)

        for field_name in mapping_values:
            if "." not in field_name:
                Convention._meta.get_field(field_name)
            elif field_name.startswith("lot."):
                Lot._meta.get_field(field_name.replace("lot.", ""))
            elif field_name.startswith("programme."):
                Programme._meta.get_field(field_name.replace("programme.", ""))
            else:
                assert f"missing test for field mapping entry: {field_name}"
