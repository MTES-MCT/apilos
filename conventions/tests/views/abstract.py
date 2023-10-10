from django.urls import reverse

from conventions.models import Convention


class AbstractCreateViewTestCase:
    # Should be used with TestCase class as a Mixin class
    convention_75: Convention
    target_path: str
    next_target_starts_with: str | None = None
    target_template: str | None
    error_payload: dict
    success_payload: dict
    msg_prefix: str
    post_success_http_code: int = 302
    post_error_http_code: int = 200
    get_expected_http_code: int = 200

    def setUp(self):
        self.convention_75 = Convention.objects.filter(numero="0001").first()
        self.target_path = ""
        self.target_template = ""
        self.error_payload = {}
        self.success_payload = {}
        self.msg_prefix = "[ViewTests] "

    def _test_data_integrity(self):
        pass

    def _test_redirect(self, response):
        if self.next_target_starts_with:
            self.assertTrue(response.url.startswith(self.next_target_starts_with))

    def _login_as_superuser(self):
        self.client.login(username="nicolas", password="12345")

    def test_view_not_logged(self):
        # user not logged -> redirect to login
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 302, msg=f"{self.msg_prefix}")
        self.assertRedirects(
            response,
            f'{reverse("login")}?next={self.target_path}',
            msg_prefix=self.msg_prefix,
        )

    def test_view_superuser(self):
        self._login_as_superuser()

        response = self.client.get(self.target_path)
        self.assertEqual(
            response.status_code, self.get_expected_http_code, msg=f"{self.msg_prefix}"
        )

        response = self.client.post(self.target_path, self.success_payload)
        self.assertEqual(
            response.status_code, self.post_success_http_code, msg=f"{self.msg_prefix}"
        )

        self._test_redirect(response)
        self._test_data_integrity()

        response = self.client.post(
            self.target_path,
            self.error_payload,
        )
        self.assertEqual(
            response.status_code, self.post_error_http_code, msg=f"{self.msg_prefix}"
        )

        if self.target_template is not None:
            self.assertTemplateUsed(
                response, self.target_template, msg_prefix=self.msg_prefix
            )

        self._test_data_integrity()

    def test_view_instructeur_ok(self):
        # login as user_instructeur_paris
        response = self.client.post(
            reverse("login"), {"username": "fix", "password": "654321"}
        )
        response = self.client.get(self.target_path)
        self.assertEqual(
            response.status_code, self.get_expected_http_code, msg=f"{self.msg_prefix}"
        )

        response = self.client.post(self.target_path, self.success_payload)
        self.assertEqual(
            response.status_code, self.post_success_http_code, msg=f"{self.msg_prefix}"
        )
        self._test_redirect(response)

    def test_view_bailleur_ok(self):
        # login as non bailleur user
        response = self.client.post(
            reverse("login"), {"username": "raph", "password": "12345"}
        )
        response = self.client.get(self.target_path)
        self.assertEqual(
            response.status_code, self.get_expected_http_code, msg=f"{self.msg_prefix}"
        )

        response = self.client.post(self.target_path, self.success_payload)
        self.assertEqual(
            response.status_code, self.post_success_http_code, msg=f"{self.msg_prefix}"
        )
        self._test_redirect(response)


class AbstractEditViewTestCase(AbstractCreateViewTestCase):
    # Should be used with TestCase class as a Mixin class
    next_target_path: str

    def setUp(self):
        super().setUp()
        self.next_target_path = ""

    def _test_redirect(self, response):
        self.assertRedirects(
            response, self.next_target_path, msg_prefix=self.msg_prefix
        )

    def test_view_instructeur_ko(self):
        # login as user_instructeur_metropole
        self.client.post(
            reverse("login"),
            {"username": "roger", "password": "567890"},
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 403, msg=f"{self.msg_prefix}")

        response = self.client.post(self.target_path)
        self.assertEqual(response.status_code, 403, msg=f"{self.msg_prefix}")

    def test_view_bailleur_ko(self):
        # login as non bailleur user
        self.client.post(
            reverse("login"),
            {"username": "sophie", "password": "567890"},
        )
        response = self.client.get(self.target_path)
        self.assertEqual(response.status_code, 403, msg=f"{self.msg_prefix}")

        response = self.client.post(self.target_path)
        self.assertEqual(response.status_code, 403, msg=f"{self.msg_prefix}")
