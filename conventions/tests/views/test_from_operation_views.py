from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from unittest_parametrize import ParametrizedTestCase, param, parametrize

from conventions.views.convention_form_from_operation import Stepper


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
                    "current_step": "Sélectioner l'opération",
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
        assert Stepper().get_form_step(step_number) == expected


class SelectOperationViewTest(TestCase):
    def basic_test(self):
        response = self.client.get(
            reverse("conventions:from_operation_select_operation")
        )
        assert response.status_code == 200

    # TODO: add tests


class AddConventionViewTest(TestCase):
    def basic_test(self):
        response = self.client.get(
            reverse("conventions:from_operation_add_convention", args=["123"])
        )
        assert response.status_code == 200

    # TODO: add tests


class AddAvenantsViewTest(TestCase):
    def basic_test(self):
        response = self.client.get(
            reverse("conventions:from_operation_add_avenants", args=["123"])
        )
        assert response.status_code == 200

    # TODO: add tests