from io import StringIO
from unittest.mock import Mock, patch

from celery import states
from celery.result import EagerResult
from django.core.management import call_command
from django.test import TestCase
from unittest_parametrize import ParametrizedTestCase, parametrize


class SendMonthlyEmailsCommandTest(ParametrizedTestCase, TestCase):
    @parametrize(
        "command_args, task_result, expected_no_verify_param, output_expected",
        [
            (
                [],
                EagerResult(
                    id="123",
                    ret_value=None,
                    state=states.SUCCESS,
                ),
                False,
                False,
            ),
            (
                ["--force"],
                EagerResult(
                    id="123",
                    ret_value=None,
                    state=states.SUCCESS,
                ),
                True,
                False,
            ),
            (
                [],
                EagerResult(
                    id="123",
                    ret_value={"instructeur": 4, "bailleur": 2},
                    state=states.SUCCESS,
                ),
                False,
                True,
            ),
        ],
    )
    def test_task_called(
        self, command_args, task_result, expected_no_verify_param, output_expected
    ):
        with patch(
            "users.tasks.send_monthly_emails.delay", Mock(return_value=task_result)
        ) as mock_task_delay:

            stdout = StringIO()
            call_command("send_monthly_emails", *command_args, stdout=stdout)
            output = stdout.getvalue().strip()

            mock_task_delay.assert_called_once_with(no_verify=expected_no_verify_param)

            if output_expected:
                assert "email(s) instructeur envoyé(s)" in output
                assert "email(s) bailleur envoyé(s)" in output
            else:
                assert "email(s) instructeur envoyé(s)" not in output
                assert "email(s) bailleur envoyé(s)" not in output
