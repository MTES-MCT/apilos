from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup
from django.test import Client
from django.urls import reverse


class TestContactView:

    def test_do_not_need_login_to_access_contact_form(self):
        """
        Test displaying convention list as superuser without filter nor order
        """

        client = Client()
        response = client.get(reverse("contact"))

        assert response.status_code == 200

        soup = BeautifulSoup(response.content, "html.parser")

        assert soup.find("input", {"name": "name"})
        assert soup.find("input", {"name": "email"})
        assert soup.find("input", {"name": "subject"})
        assert soup.find("textarea", {"name": "message"})
        assert soup.find("button", {"type": "submit"})

    @pytest.mark.django_db
    def test_post_contact_form_sends_email(self):
        """
        Test that posting the contact form sends an email.
        """
        with patch("django.core.mail.EmailMultiAlternatives.send") as mock_send:

            client = Client()
            form_data = {
                "name": "Test Name",
                "email": "test@example.com",
                "subject": "Test Subject",
                "message": "Test message",
            }
            response = client.post(reverse("contact"), data=form_data)

            # Check that the response is a redirect (to the same contact page, typically)
            assert response.status_code == 302

            # Check that EmailMultiAlternatives.send() was called
            assert mock_send.called
