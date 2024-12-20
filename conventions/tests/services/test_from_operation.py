import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from unittest_parametrize import ParametrizedTestCase, param, parametrize

from bailleurs.tests.factories import BailleurFactory
from conventions.models import ConventionStatut
from conventions.services.from_operation import (
    AddAvenantsService,
    AddConventionService,
    Operation,
    SelectOperationService,
)
from conventions.services.utils import ReturnStatus
from conventions.tests.factories import AvenantTypeFactory, ConventionFactory
from core.tests.test_utils import PGTrgmTestMixin
from programmes.models import Financement, NatureLogement
from programmes.tests.factories import ProgrammeFactory
from siap.siap_client.mock_data import operation_mock
from users.tests.factories import UserFactory


@override_settings(USE_MOCKED_SIAP_CLIENT=True)
class TestSelectOperationService(PGTrgmTestMixin, ParametrizedTestCase, TestCase):
    def setUp(self):
        self.request = RequestFactory()
        self.request.user = UserFactory(cerbere=True, is_superuser=True)
        self.request.session = {"habilitation_id": 5}

        ProgrammeFactory(
            uuid="67062edc-3ee8-4262-965f-98f885d418f4",
            numero_operation="2017DD01100057",
            nom="Programme 1",
            nature_logement=NatureLogement.LOGEMENTSORDINAIRES,
            ville="Bayonne",
            bailleur__nom="Bailleur A",
        )
        ProgrammeFactory(
            uuid="7fb89bd6-62f8-4c06-b15a-4fc81bc02995",
            numero_operation="2017DD01201254",
            nom="Programme 3",
            nature_logement=NatureLogement.RESISDENCESOCIALE,
            ville="L'Isle-sur-la-Sorgue",
            bailleur__nom="Bailleur B",
        )

    @parametrize(
        "numero_operation, expected_matching, expected_operations",
        [
            param(
                "20220600006",
                True,
                [
                    Operation(
                        numero="20220600006",
                        nom="Programme 2",
                        bailleur="3F",
                        nature="LOO",
                        commune="Marseille",
                        siap_payload=operation_mock,
                    )
                ],
                id="siap_match_exact",
            ),
            param(
                "2017DD01100057",
                True,
                [
                    Operation(
                        numero="2017DD01100057",
                        nom="Programme 1",
                        bailleur="Bailleur A",
                        nature="Logements ordinaires",
                        commune="Bayonne",
                        siap_payload=None,
                    )
                ],
                id="apilos_match_exact",
            ),
            param(
                "2017DD01",
                False,
                [
                    Operation(
                        numero="2017DD01201254",
                        nom="Programme 3",
                        bailleur="Bailleur B",
                        nature="Résidence sociale",
                        commune="L'Isle-sur-la-Sorgue",
                        siap_payload=None,
                    ),
                    Operation(
                        numero="2017DD01100057",
                        nom="Programme 1",
                        bailleur="Bailleur A",
                        nature="Logements ordinaires",
                        commune="Bayonne",
                        siap_payload=None,
                    ),
                ],
                id="apilos_search_trgrm",
            ),
        ],
    )
    def test_fetch_operations(
        self, numero_operation, expected_matching, expected_operations
    ):
        service = SelectOperationService(
            request=self.request, numero_operation=numero_operation
        )
        exact_match, operations = service.fetch_operations()
        assert exact_match == expected_matching
        assert operations == expected_operations


class TestAddConventionService(TestCase):
    def basic_test(self):
        service = AddConventionService(request=RequestFactory())
        assert service.form is not None


class TestAddAvenantsService(TestCase):
    def setUp(self):
        self.request = RequestFactory()
        self.request.user = UserFactory(cerbere=True, is_superuser=True)
        self.request.session = {"habilitation_id": 5}

        self.bailleur = BailleurFactory(
            uuid="8e01af98-358f-4cb5-a8ae-9597d10f571b",
        )

        self.convention = ConventionFactory(
            uuid="5611304e-74d6-41ab-8f9d-2d0c27563e9a",
            numero="33N611709S700029",
            statut=ConventionStatut.SIGNEE.label,
            financement=Financement.PLUS,
            televersement_convention_signee_le="2024-01-01",
            programme=ProgrammeFactory(bailleur=self.bailleur),
            create_lot=True,
            create_lot__nb_logements=100,
        )
        assert self.convention.lot.nb_logements == 100

        self.user = UserFactory(cerbere=True, is_superuser=True)

        AvenantTypeFactory(nom="bailleur")
        AvenantTypeFactory(nom="champ_libre")
        AvenantTypeFactory(nom="logements")

    def test_form_with_get_request(self):
        request = RequestFactory().get(path="/whatever")
        request.user = self.user

        service = AddAvenantsService(request=request, convention=self.convention)
        assert service.form.data.dict() == {}
        assert service.form.fields["bailleur"].queryset.count() == 1
        assert service.form.fields["bailleur"].queryset.first() == self.bailleur
        assert service.form.initial == {
            "bailleur": self.bailleur,
            "nb_logements": 100,
        }

    def test_form_with_post_request(self):
        request = RequestFactory().post(
            path="/whatever",
            data={
                "numero": "1234",
                "annee_signature": 2024,
            },
        )
        request.user = self.user

        service = AddAvenantsService(request=request, convention=self.convention)
        assert service.form.data.dict() == {
            "numero": "1234",
            "annee_signature": "2024",
        }
        assert service.form.fields["bailleur"].queryset.count() == 1
        assert service.form.fields["bailleur"].queryset.first() == self.bailleur

    def test_save_invalid_form(self):
        request = RequestFactory().post(path="/whatever", data={"numero": "1234"})
        request.user = self.user

        service = AddAvenantsService(request=request, convention=self.convention)
        assert service.save() == ReturnStatus.ERROR

    def test_save_valid_form(self):
        # bailleur_2 = BailleurFactory()

        request = RequestFactory().post(
            path="/whatever",
            data={
                "numero": "1234",
                "annee_signature": 2024,
                "champ_libre_avenant": "mon commentaire",
                "nb_logements": 102,
                # "bailleur": bailleur_2.uuid
            },
        )
        request.user = self.user

        with tempfile.NamedTemporaryFile(mode="wb") as upload_file:
            upload_file.write(b'{"whatever": "content"}')
            upload_file.seek(0)
            with open(upload_file.name, "rb") as f:
                request.FILES["nom_fichier_signe"] = SimpleUploadedFile(
                    f.name, f.read()
                )

        service = AddAvenantsService(request=request, convention=self.convention)
        result = service.save()
        form_errors = service.form.errors
        assert result == ReturnStatus.SUCCESS, f"Errors: {form_errors}"

        avenant = self.convention.avenants.first()
        assert avenant.numero == "1234"
        assert avenant.champ_libre_avenant == "mon commentaire"
        # FIXME
        # assert avenant.lot.nb_logements == 102
        # assert avenant.bailleur == bailleur_2

        assert sorted(list(avenant.avenant_types.values_list("nom", flat=True))) == [
            # "bailleur",
            "champ_libre",
            "logements",
        ]
