import unittest
from siap.siap_client import utils


class UtilsTest(unittest.TestCase):

    # Test model User
    def test__address_interpretation(self):
        # pylint: disable=W0212
        adresse, code_postal, ville = utils._address_interpretation("")
        self.assertEqual(adresse, "")
        self.assertEqual(code_postal, "")
        self.assertEqual(ville, "")
        adresse, code_postal, ville = utils._address_interpretation(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        )
        self.assertEqual(
            adresse, "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        )
        self.assertEqual(code_postal, "")
        self.assertEqual(ville, "")
        adresse, code_postal, ville = utils._address_interpretation(
            "145, rue des chamallow  13015 MarSeille CEDEX 15"
        )
        self.assertEqual(adresse, "145, rue des chamallow")
        self.assertEqual(code_postal, "13015")
        self.assertEqual(ville, "MarSeille CEDEX 15")
