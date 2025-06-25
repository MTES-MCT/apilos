from unittest import mock

import pytest
import time_machine
from django.test import RequestFactory, SimpleTestCase
from unittest_parametrize import ParametrizedTestCase, parametrize

from conventions.models import ConventionStatut
from conventions.services.utils import convention_upload_filename, delete_action_alertes
from core.tests.factories import ConventionFactory
from siap.siap_client.client import SIAPClient
from conventions.services.utils import (
    convention_upload_filename,
    get_convention_export_excel_header,
    get_convention_export_excel_row,
)
from core.tests.factories import (
    ConventionFactory,
    LogementFactory,
    LotFactory,
)
from users.tests.factories import UserFactory

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


@pytest.mark.django_db
def test_get_convention_export_excel_header():
    request = RequestFactory().get("/")
    user = UserFactory()
    user.is_instructeur = True
    request.user = user

    header = get_convention_export_excel_header(request)

    expected_header_instructeur = [
        "Année de gestion",
        "Numéro d'opération SIAP",
        "Numéro de convention",
        "Commune",
        "Code postal",
        "Nom de l'opération",
        "Instructeur",
        "Type de financement",
        "Nombre de logements",
        "Nature de l'opération",
        "Date de signature",
        "Montant du loyer au m2",
        "Livraison",
    ]

    assert header == expected_header_instructeur

    user.is_instructeur = False
    request.user = user
    header = get_convention_export_excel_header(request)

    assert header[6] == "Bailleur"
    assert len(header) == 13


@pytest.mark.django_db
def test_get_convention_export_excel_row():
    lot = LotFactory()
    logement = LogementFactory(lot=lot)
    convention = ConventionFactory()
    convention.logements = [logement]
    convention.save()
    lot.convention = convention
    lot.save()

    request = RequestFactory().get("/")
    user = UserFactory()
    user.is_instructeur = True
    request.user = user

    row = get_convention_export_excel_row(request, convention)

    assert len(row) == 13

    assert row[0] == convention.programme.annee_gestion_programmation
    assert row[1] == convention.programme.numero_operation
    assert row[2] == convention.numero
    assert row[3] == convention.programme.ville
    assert row[4] == convention.programme.code_postal
    assert row[5] == convention.programme.nom
    assert row[6] == convention.programme.administration.nom
    assert row[7] == convention.lot.get_financement_display()
    assert row[8] == convention.lot.nb_logements
    assert row[9] == convention.programme.nature_logement
    assert convention.televersement_convention_signee_le is None and row[10] == "-"
    assert row[11] == logement.loyer_par_metre_carre
    assert row[12] == convention.programme.date_achevement_compile.strftime("%d/%m/%Y")

    user.is_instructeur = False
    request.user = user
    row = get_convention_export_excel_row(request, convention)

    assert len(row) == 13

    assert row[6] == convention.programme.bailleur.nom


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
