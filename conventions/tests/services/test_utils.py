import pytest
import time_machine
from django.test import RequestFactory, SimpleTestCase
from unittest_parametrize import ParametrizedTestCase, parametrize

from conventions.models import ConventionStatut
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
def test_get_convention_export_excel_header():
    request = RequestFactory().get("/")
    user = UserFactory()
    user.is_instructeur = True
    request.user = user

    header = get_convention_export_excel_header(request)

    expected_header_instructeur = [
        "Numéro d'opération SIAP",
        "Numéro de convention",
        "Numéro d'avenant",
        "Statut de la convention",
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
        "date de fin de conventionnement",
    ]

    assert header == expected_header_instructeur

    user.is_instructeur = False
    request.user = user
    header = get_convention_export_excel_header(request)

    assert header[7] == "Bailleur"
    assert len(header) == 15


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

    assert row == [
        convention.programme.numero_operation,
        convention.numero,
        "",
        convention.statut,
        convention.programme.ville,
        convention.programme.code_postal,
        convention.programme.nom,
        convention.programme.administration.nom,
        convention.lot.get_financement_display(),
        convention.lot.nb_logements,
        convention.programme.nature_logement,
        "-",
        logement.loyer_par_metre_carre,
        "11/04/2024",
        "-",
    ]

    user.is_instructeur = False
    request.user = user
    row = get_convention_export_excel_row(request, convention)

    assert len(row) == 15

    assert row[7] == convention.programme.bailleur.nom


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
