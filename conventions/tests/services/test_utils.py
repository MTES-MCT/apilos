import time_machine
from django.test import SimpleTestCase
from unittest_parametrize import ParametrizedTestCase, parametrize

from conventions.models import ConventionStatut
from conventions.services.utils import convention_upload_filename
from conventions.tests.factories import ConventionFactory


class UtilsTest(ParametrizedTestCase, SimpleTestCase):

    @parametrize(
        "conv_data, expected_result",
        [
            (
                {
                    "numero": "123/456/789",
                },
                "convention_123/456/789_projet_2024-06-21_00-00_signed.pdf",
            ),
            (
                {
                    "numero": None,
                },
                "convention_NUM_projet_2024-06-21_00-00_signed.pdf",
            ),
            (
                {
                    "numero": "",
                },
                "convention_NUM_projet_2024-06-21_00-00_signed.pdf",
            ),
            (
                {
                    "numero": "123 456 789",
                    "statut": ConventionStatut.INSTRUCTION.label,
                },
                "convention_123_456_789_2024-06-21_00-00_signed.pdf",
            ),
            (
                {
                    "numero": "1",
                    "parent": ConventionFactory.build(numero="123/456/789"),
                },
                "convention_123/456/789_avenant_1_projet_2024-06-21_00-00_signed.pdf",
            ),
            (
                {
                    "numero": None,
                    "parent": ConventionFactory.build(numero="123/456/789"),
                },
                "convention_123/456/789_avenant_N_projet_2024-06-21_00-00_signed.pdf",
            ),
            (
                {
                    "numero": "",
                    "parent": ConventionFactory.build(numero="123/456/789"),
                },
                "convention_123/456/789_avenant_N_projet_2024-06-21_00-00_signed.pdf",
            ),
        ],
    )
    def test_convention_upload_filename(self, conv_data, expected_result):
        with time_machine.travel("2024-06-21"):
            assert (
                convention_upload_filename(
                    convention=ConventionFactory.build(**conv_data)
                )
                == expected_result
            )
