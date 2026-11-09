from django.conf import settings
from django.test import SimpleTestCase

from core.settings import get_content_security_policy


class SecuritySettingsTests(SimpleTestCase):
    def test_hsts_is_disabled_by_default_but_includes_subdomains_and_preload(self):
        self.assertEqual(settings.SECURE_HSTS_SECONDS, 0)
        self.assertTrue(settings.SECURE_HSTS_INCLUDE_SUBDOMAINS)
        self.assertTrue(settings.SECURE_HSTS_PRELOAD)

    def test_swagger_ui_csp_directives_depend_on_debug(self):
        swagger_sources = [
            (
                "img-src",
                "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/favicon-32x32.png",
            ),
            (
                "script-src",
                "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-bundle.js",
            ),
            (
                "script-src",
                "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui-standalone-preset.js",
            ),
            (
                "style-src",
                "https://cdn.jsdelivr.net/npm/swagger-ui-dist@latest/swagger-ui.css",
            ),
        ]
        dev_directives = get_content_security_policy(debug=True)["DIRECTIVES"]
        prod_directives = get_content_security_policy(debug=False)["DIRECTIVES"]

        for directive, source in swagger_sources:
            self.assertIn(source, dev_directives[directive])
            self.assertNotIn(source, prod_directives[directive])
