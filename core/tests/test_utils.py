import unittest
import uuid

from core.utils import round_half_up, is_valid_uuid, get_key_from_json_field


class UtilsTest(unittest.TestCase):
    def test_round_half_up(self):
        self.assertEqual(round_half_up(1), 1)
        self.assertEqual(round_half_up(0.5), 1)
        self.assertEqual(round_half_up(1.5), 2)
        self.assertEqual(round_half_up(0.49999999999), 0)
        self.assertEqual(round_half_up(1.49999999999), 1)
        self.assertEqual(round_half_up(1, ndigits=2), 1)
        self.assertEqual(round_half_up(0.5, ndigits=2), 0.5)
        self.assertEqual(round_half_up(1.5, ndigits=2), 1.5)
        self.assertEqual(round_half_up(0.49999999999, ndigits=2), 0.5)
        self.assertEqual(round_half_up(1.49999999999, ndigits=2), 1.5)
        self.assertEqual(round_half_up(0.005, ndigits=2), 0.01)
        self.assertEqual(round_half_up(1.005, ndigits=2), 1.01)
        self.assertEqual(round_half_up(0.0049999999999, ndigits=2), 0)
        self.assertEqual(round_half_up(1.0049999999999, ndigits=2), 1)

    def test_is_valid_uuid(self):
        self.assertFalse(is_valid_uuid(1))
        self.assertFalse(is_valid_uuid("123-UUID-wannabe"))
        self.assertFalse(is_valid_uuid({"A": "b"}))
        self.assertFalse(is_valid_uuid([1, 2, 3]))

        self.assertTrue(is_valid_uuid(uuid.uuid4()))
        self.assertTrue(is_valid_uuid(str(uuid.uuid4())))
        self.assertTrue(is_valid_uuid(uuid.uuid4().hex))
        self.assertTrue(is_valid_uuid(uuid.uuid3(uuid.NAMESPACE_DNS, "example.net")))
        self.assertTrue(is_valid_uuid(uuid.uuid5(uuid.NAMESPACE_DNS, "example.net")))
        self.assertTrue(is_valid_uuid("{20f5484b-88ae-49b0-8af0-3a389b4917dd}"))
        self.assertTrue(is_valid_uuid("20f5484b88ae49b08af03a389b4917dd"))

    def test_get_key_from_json_field(self):
        # get_key_from_json_field(json_field, key, default="")
        self.assertEqual(get_key_from_json_field("n'imp", "mykey"), "")
        self.assertEqual(get_key_from_json_field(None, "mykey"), "")
        self.assertEqual(get_key_from_json_field(1, "mykey"), "")
        self.assertEqual(get_key_from_json_field({"othherkey": "ok"}, "mykey"), "")
        self.assertEqual(
            get_key_from_json_field(["mykey", "othherkey", "ok"], "mykey"), ""
        )

        self.assertEqual(
            get_key_from_json_field("n'imp", "mykey", default="myvalue"), "myvalue"
        )
        self.assertEqual(
            get_key_from_json_field(None, "mykey", default="myvalue"), "myvalue"
        )
        self.assertEqual(
            get_key_from_json_field(1, "mykey", default="myvalue"), "myvalue"
        )
        self.assertEqual(
            get_key_from_json_field({"othherkey": "ok"}, "mykey", default="myvalue"),
            "myvalue",
        )
        self.assertEqual(
            get_key_from_json_field(
                ["mykey", "othherkey", "ok"], "mykey", default="myvalue"
            ),
            "myvalue",
        )
        self.assertEqual(
            get_key_from_json_field({"mykey": "ok"}, "mykey", default="myvalue"),
            "myvalue",
        )

        self.assertEqual(
            get_key_from_json_field('{"mykey": "ok"}', "mykey", default="myvalue"),
            "ok",
        )
        self.assertEqual(
            get_key_from_json_field('{"mykey": 1}', "mykey", default="myvalue"),
            1,
        )
        self.assertEqual(
            get_key_from_json_field('{"mykey": true}', "mykey", default="myvalue"),
            True,
        )
        self.assertEqual(
            get_key_from_json_field('{"mykey": null}', "mykey", default="myvalue"),
            None,
        )
        self.assertEqual(
            get_key_from_json_field(
                '{"mykey": {"myokey": "myovalue"}}', "mykey", default="myvalue"
            ),
            {"myokey": "myovalue"},
        )
