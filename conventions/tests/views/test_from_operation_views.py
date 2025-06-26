from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from unittest_parametrize import ParametrizedTestCase, param, parametrize

from conventions.forms.convention_from_operation import AddAvenantForm
from conventions.models import Convention, ConventionStatut
from conventions.services.utils import ReturnStatus
from conventions.views.convention_form_from_operation import FromOperationBaseView
from core.tests.factories import ConventionFactory


class StepperTest(ParametrizedTestCase, SimpleTestCase):
    @parametrize(
        "step_number, expected",
        [
            param(
                0,
                None,
                id="step_0",
            ),
            param(
                1,
                {
                    "current_step": "Sélectionner l'opération",
                    "next_step": "Créer la convention dans Apilos",
                    "number": 1,
                    "total": 3,
                },
                id="step_1",
            ),
            param(
                2,
                {
                    "current_step": "Créer la convention dans Apilos",
                    "next_step": "Ajouter les avenants (optionnel)",
                    "number": 2,
                    "total": 3,
                },
                id="step_2",
            ),
            param(
                3,
                {
                    "current_step": "Ajouter les avenants (optionnel)",
                    "next_step": None,
                    "number": 3,
                    "total": 3,
                },
                id="step_3",
            ),
            param(
                4,
                None,
                id="step_4",
            ),
        ],
    )
    def test_get_form_step(self, step_number, expected):
        request = RequestFactory().get("/")
        base_view = FromOperationBaseView()
        base_view.setup(request)
        assert base_view.stepper.get_form_step(step_number) == expected


@override_settings(USE_MOCKED_SIAP_CLIENT=True)
class SelectOperationViewTest(TestCase):
    fixtures = [
        "auth.json",
        "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def _login(self):
        assert self.client.login(username="nicolas", password="12345")

        session = self.client.session
        session["habilitation_id"] = 5
        session.save()

    def test_basic(self):
        self._login()

        response = self.client.get(reverse("conventions:from_operation_select"))
        assert response.status_code == 200

    # TODO: add tests


@override_settings(USE_MOCKED_SIAP_CLIENT=True)
class AddConventionViewTest(TestCase):
    fixtures = [
        "auth.json",
        "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def _login(self):
        assert self.client.login(username="nicolas", password="12345")

        session = self.client.session
        session["habilitation_id"] = 5
        session.save()

    def test_redirect_if_numero_operaion_is_unknown(self):
        self._login()

        response = self.client.get(
            reverse("conventions:from_operation_add_convention", args=["123"])
        )
        assert response.status_code == 302
        assertRedirects(response, reverse("conventions:from_operation_select"))

    # TODO: add tests


class AddAvenantsViewTest(TestCase):
    fixtures = [
        "auth.json",
        "departements.json",
        "avenant_types.json",
        "bailleurs_for_tests.json",
        "instructeurs_for_tests.json",
        "programmes_for_tests.json",
        "conventions_for_tests.json",
        "users_for_tests.json",
    ]

    def setUp(self) -> None:
        self.convention = Convention.objects.filter(
            uuid="f590c593-e37f-4258-b38a-f8d2869969c4"
        ).first()
        assert self.convention is not None

        self.convention.statut = ConventionStatut.SIGNEE.label
        self.convention.save()

        self.avenant = ConventionFactory(parent=self.convention)

    def _login(self):
        assert self.client.login(username="nicolas", password="12345")

    def test_convention_not_found(self):
        self._login()

        response = self.client.get(
            reverse(
                "conventions:from_operation_add_avenants",
                args=["60d1fc70-f652-4645-8147-05c8ab27ade9"],
            )
        )

        assert response.status_code == 404

    @patch("conventions.services.from_operation.AddAvenantsService.save")
    def test_get_context_data(self, mock_service_save):
        self._login()

        response = self.client.get(
            reverse(
                "conventions:from_operation_add_avenants",
                args=["f590c593-e37f-4258-b38a-f8d2869969c4"],
            )
        )

        assert response.status_code == 200
        mock_service_save.assert_not_called()
        assert response.context["convention"] == self.convention
        assert list(response.context["avenants"]) == [self.avenant]
        assert isinstance(response.context["form"], AddAvenantForm)

    @patch("conventions.services.from_operation.AddAvenantsService.save")
    def test_post_with_error(self, mock_service_save):
        mock_service_save.return_value = ReturnStatus.ERROR

        self._login()
        response = self.client.post(
            reverse(
                "conventions:from_operation_add_avenants",
                args=["f590c593-e37f-4258-b38a-f8d2869969c4"],
            ),
            data={},
        )

        assert response.status_code == 200
        mock_service_save.assert_called_once()
        assert response.context["convention"] == self.convention

    @patch("conventions.services.from_operation.AddAvenantsService.save")
    def test_post_no_error(self, mock_service_save):
        mock_service_save.return_value = ReturnStatus.SUCCESS

        self._login()
        response = self.client.post(
            reverse(
                "conventions:from_operation_add_avenants",
                args=["f590c593-e37f-4258-b38a-f8d2869969c4"],
            ),
            data={},
        )

        assert response.status_code == 302
        mock_service_save.assert_called_once()
