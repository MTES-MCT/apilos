from django.conf import settings
from django.test import SimpleTestCase


class SecuritySettingsTests(SimpleTestCase):
    def test_hsts_is_disabled_by_default_but_includes_subdomains_and_preload(self):
        self.assertEqual(settings.SECURE_HSTS_SECONDS, 0)
        self.assertTrue(settings.SECURE_HSTS_INCLUDE_SUBDOMAINS)
        self.assertTrue(settings.SECURE_HSTS_PRELOAD)
