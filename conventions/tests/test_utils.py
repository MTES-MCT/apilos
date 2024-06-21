import time_machine

from conventions.services.utils import convention_upload_filename
from conventions.tests.factories import ConventionFactory


@time_machine.travel("2024-06-21")
def test_convention_upload_filename():
    assert (
        convention_upload_filename(
            ConventionFactory.build(uuid="827dc499-cce3-4efb-b5e9-cc76280773b2")
        )
        == "2024-06-21_00-00_convention_827dc499-cce3-4efb-b5e9-cc76280773b2_signed.pdf"
    )
