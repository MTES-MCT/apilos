from unittest import mock

import pytest
import time_machine
from django.test import SimpleTestCase
from unittest_parametrize import ParametrizedTestCase, parametrize

from conventions.models import ConventionStatut
from conventions.services.utils import convention_upload_filename, delete_action_alertes
from core.tests.factories import ConventionFactory
from siap.siap_client.client import SIAPClient


@pytest.mark.django_db
def test_delete_action_alertes():
    convention = ConventionFactory()
    siap_credentials = {"habilitation_id": "001", "user_login": 1}

    with mock.patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_client = mock.MagicMock()
        mock_get_instance.return_value = mock_client
        mock_client.list_convention_alertes.return_value = [
            {"id": 1, "categorie": "CATEGORIE_ALERTE_ACTION"},
            {"id": 2, "categorie": "CATEGORIE_ALERTE_INFORMATION"},
        ]
        delete_action_alertes(convention, siap_credentials)

        mock_client.delete_alerte.assert_called_once()
        assert mock_client.delete_alerte.mock_calls[0].kwargs["alerte_id"] == 1


@pytest.mark.django_db
def test_delete_action_alertes_for_instructeur():
    convention = ConventionFactory()
    siap_credentials = {"habilitation_id": "001", "user_login": 1}

    with mock.patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_client = mock.MagicMock()
        mock_get_instance.return_value = mock_client
        mock_client.list_convention_alertes.return_value = [
            {
                "id": 1,
                "categorie": "CATEGORIE_ALERTE_ACTION",
                "destinataires": [{"codeProfil": "SER_GEST"}],
            },
            {
                "id": 2,
                "categorie": "CATEGORIE_ALERTE_ACTION",
                "destinataires": [{"codeProfil": "MO_PERS_MORALE"}],
            },
            {
                "id": 3,
                "categorie": "CATEGORIE_ALERTE_ACTION",
                "destinataires": [{"codeProfil": "SER_GEST"}],
            },
        ]
        delete_action_alertes(convention, siap_credentials, "SG")

        mock_client.delete_alerte.assert_called()
        assert mock_client.delete_alerte.mock_calls[0].kwargs["alerte_id"] == 1
        assert mock_client.delete_alerte.mock_calls[1].kwargs["alerte_id"] == 3


@pytest.mark.django_db
def test_delete_action_alertes_for_bailleur():
    convention = ConventionFactory()
    siap_credentials = {"habilitation_id": "001", "user_login": 1}

    with mock.patch.object(SIAPClient, "get_instance") as mock_get_instance:
        mock_client = mock.MagicMock()
        mock_get_instance.return_value = mock_client
        mock_client.list_convention_alertes.return_value = [
            {
                "id": 1,
                "categorie": "CATEGORIE_ALERTE_ACTION",
                "destinataires": [{"codeProfil": "SER_GEST"}],
            },
            {
                "id": 2,
                "categorie": "CATEGORIE_ALERTE_ACTION",
                "destinataires": [{"codeProfil": "MO_PERS_MORALE"}],
            },
            {
                "id": 3,
                "categorie": "CATEGORIE_ALERTE_ACTION",
                "destinataires": [{"codeProfil": "SER_GEST"}],
            },
        ]
        delete_action_alertes(convention, siap_credentials, "MO")

        mock_client.delete_alerte.assert_called_once()
        assert mock_client.delete_alerte.mock_calls[0].kwargs["alerte_id"] == 2


class UtilsTest(ParametrizedTestCase, SimpleTestCase):

    @parametrize(
        "conv_data, expected_result",
        [
            (
                {
                    "numero": "123/456/789",
                },
                "convention_123/456/789_projet_2024-06-21_00-00.pdf",
            ),
            (
                {
                    "numero": None,
                },
                "convention_NUM_projet_2024-06-21_00-00.pdf",
            ),
            (
                {
                    "numero": "",
                },
                "convention_NUM_projet_2024-06-21_00-00.pdf",
            ),
            (
                {
                    "numero": "123 456 789",
                    "statut": ConventionStatut.INSTRUCTION.label,
                },
                "convention_123_456_789_2024-06-21_00-00.pdf",
            ),
            (
                {
                    "numero": "1",
                    "parent": ConventionFactory.build(numero="123/456/789"),
                },
                "convention_123/456/789_avenant_1_projet_2024-06-21_00-00.pdf",
            ),
            (
                {
                    "numero": None,
                    "parent": ConventionFactory.build(numero="123/456/789"),
                },
                "convention_123/456/789_avenant_N_projet_2024-06-21_00-00.pdf",
            ),
            (
                {
                    "numero": "",
                    "parent": ConventionFactory.build(numero="123/456/789"),
                },
                "convention_123/456/789_avenant_N_projet_2024-06-21_00-00.pdf",
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
