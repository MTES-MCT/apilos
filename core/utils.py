from typing import SupportsRound, Any


def round_half_up(number: SupportsRound[Any], ndigits: int = 0):
    """
    python 3 round number following "round half to even" way
    It doesn't fit the UE norm which is a "round half up" way
    round_half_up follow the UE norm way of round
    """
    if ndigits == 0:
        return round(float(number) + 1e-15)
    return round(float(number) + 1e-15, ndigits)
