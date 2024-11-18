from unittest.mock import patch

import time_machine
from django.test import TestCase, override_settings
from unittest_parametrize import ParametrizedTestCase, param, parametrize

from users.tasks import send_monthly_emails


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class SendMonthlyEmailsTaskTest(ParametrizedTestCase, TestCase):

    @parametrize(
        "travel_to, call_expected",
        [
            param("2023-04-11", False, id="not_monday"),
            param("2023-04-10", False, id="monday_but_not_first_of_month"),
            param("2023-04-03", True, id="first_monday_of_month"),
        ],
    )
    @override_settings(CRON_ENABLED=True)
    @override_settings(APPLICATION_DOMAIN_URL="http://localhost:8001")
    def test_first_monday_of_month(self, travel_to, call_expected):
        with (
            time_machine.travel(travel_to),
            patch("users.tasks.UserService.email_mensuel") as mock_email_mensuel,
        ):
            send_monthly_emails.delay()

        if call_expected:
            mock_email_mensuel.assert_called_once()
        else:
            mock_email_mensuel.assert_not_called()

    @time_machine.travel("2023-04-03")
    @override_settings(APPLICATION_DOMAIN_URL="http://localhost:8001")
    @patch("users.tasks.UserService.email_mensuel")
    def test_cron_disabled(self, mock_email_mensuel):
        send_monthly_emails.delay()
        mock_email_mensuel.assert_not_called()

    @time_machine.travel("2023-04-03")
    @override_settings(CRON_ENABLED=True)
    @override_settings(APPLICATION_DOMAIN_URL="")
    @patch("users.tasks.UserService.email_mensuel")
    def test_application_domain_url_is_not_set(self, mock_email_mensuel):
        send_monthly_emails.delay()
        mock_email_mensuel.assert_not_called()

    @parametrize(
        "travel_to, cron_enabled",
        [
            param("2023-04-03", False, id="bypass_cron_enabled"),
            param("2023-04-10", True, id="bypass_first_day_of_month_check"),
            param("2023-04-11", True, id="bypass_not_monday_check"),
        ],
    )
    @override_settings(APPLICATION_DOMAIN_URL="http://localhost:8001")
    def test_no_verify_param(self, travel_to, cron_enabled):
        with (
            time_machine.travel(travel_to),
            override_settings(CRON_ENABLED=cron_enabled),
            patch("users.tasks.UserService.email_mensuel") as mock_email_mensuel,
        ):
            send_monthly_emails.delay(no_verify=True)
            mock_email_mensuel.assert_called_once()

    @time_machine.travel("2023-04-03")
    @override_settings(CRON_ENABLED=True)
    @override_settings(APPLICATION_DOMAIN_URL=None)
    @patch("users.tasks.UserService.email_mensuel")
    def test_no_verify_param_and_application_domain_url(self, mock_email_mensuel):
        send_monthly_emails.delay()
        mock_email_mensuel.assert_not_called()
