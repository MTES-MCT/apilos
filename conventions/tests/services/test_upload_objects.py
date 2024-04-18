from decimal import Decimal

import pytest

from conventions.services.upload_objects import (
    _float_to_decimal_rounded_two_digits_half_up,
)


@pytest.mark.parametrize(
    "float_input,expected",
    [
        (7.505, "7.51"),
        (7.504, "7.50"),
        (7.506, "7.51"),
        (7.5049999999, "7.50"),
        # We only round well for 11 digits
        # here 12 digits -> we expect our round to fail
        (7.50499999999, "7.51"),
        # No regression
        (145.59, "145.59"),
        (145.18, "145.18"),
    ],
)
def test_float_to_decimal_rounded_two_digits_half_up(float_input, expected):
    assert _float_to_decimal_rounded_two_digits_half_up(float_input) == Decimal(
        expected
    )
