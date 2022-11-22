import random
import unittest
from conventions.services.convention_generator import pluralize


class ConventionGeneratorTest(unittest.TestCase):
    def test_pluralize(self):
        self.assertEqual(pluralize(0), "")
        self.assertEqual(pluralize(1), "")
        self.assertEqual(pluralize(2), "s")
        self.assertEqual(pluralize(random.randint(3, 999)), "s")
