from decimal import Decimal

import pytest

from conventions.services.upload_objects import (
    _float_to_decimal_rounded_half_up,
)


@pytest.mark.parametrize(
    "float_input,decimal_places,expected",
    [
        (7.505, 2, "7.51"),
        (7.504, 2, "7.50"),
        (7.506, 2, "7.51"),
        (7.50499999999, 2, "7.50"),
        (14444.59, 2, "14444.59"),
        (145.18, 2, "145.18"),
        (7.505, 3, "7.505"),
        (7.5049, 3, "7.505"),
        (7.506787, 5, "7.50679"),
        (7.65, 0, "8"),
    ],
)
def test_float_to_decimal_rounded_two_digits_half_up(
    float_input, decimal_places, expected
):
    assert _float_to_decimal_rounded_half_up(float_input, decimal_places) == Decimal(
        expected
    )
