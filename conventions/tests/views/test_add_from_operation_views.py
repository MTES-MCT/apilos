from django.test import SimpleTestCase
from unittest_parametrize import ParametrizedTestCase, param, parametrize

from conventions.views.convention_form_add_from_operation import Step, Stepper


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
                    "current_step": Step(
                        title="Sélection de l'opération",
                        pathname="conventions:select_operation",
                    ),
                    "next_step": Step(
                        title="Créer la convention dans Apilos",
                        pathname="conventions:add_convention",
                    ),
                    "number": 1,
                    "total": 3,
                },
                id="step_1",
            ),
            param(
                2,
                {
                    "current_step": Step(
                        title="Créer la convention dans Apilos",
                        pathname="conventions:add_convention",
                    ),
                    "next_step": Step(
                        title="Ajouter les avenants (optionnel)",
                        pathname="conventions:add_convention",
                    ),
                    "number": 2,
                    "total": 3,
                },
                id="step_2",
            ),
            param(
                3,
                {
                    "current_step": Step(
                        title="Ajouter les avenants (optionnel)",
                        pathname="conventions:add_convention",
                    ),
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
