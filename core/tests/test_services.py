from unittest import TestCase

from core.services import Slugifier


class SlugifierTest(TestCase):

    def test_slugify(self):
        self.assertEqual(Slugifier.slugify("Bernard de La Villardière"), "bernard-de-la-villardiere")
        self.assertEqual(Slugifier.slugify("Barbe à papa", ''), "barbeapapa")
