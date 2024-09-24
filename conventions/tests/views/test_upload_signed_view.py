import datetime

import pytest
from django.test import RequestFactory
from django.urls import reverse

from conventions.tests.factories import ConventionFactory
from conventions.views.conventions import (
    ConventionDateUploadSignedView,
    ConventionPreviewUploadSignedView,
)
from users.tests.factories import UserFactory


@pytest.mark.django_db
class TestConventionPreviewUploadSignedView:
    def test_get(self):
        convention = ConventionFactory()
        url = reverse(
            "conventions:preview_upload_signed",
            kwargs={"convention_uuid": convention.uuid},
        )
        request = RequestFactory().get(url)
        user = UserFactory(is_superuser=True)
        request.user = user
        request.session = "session"

        response = ConventionPreviewUploadSignedView.as_view()(
            request, convention_uuid=convention.uuid
        )

        assert response.status_code == 200


@pytest.mark.django_db
class TestConventionDateUploadSignedView:
    def test_get(self):
        convention = ConventionFactory()
        url = reverse(
            "conventions:preview_upload_signed",
            kwargs={"convention_uuid": convention.uuid},
        )
        request = RequestFactory().get(url)
        user = UserFactory(is_superuser=True)
        request.user = user
        request.session = "session"

        response = ConventionDateUploadSignedView.as_view()(
            request, convention_uuid=convention.uuid
        )

        assert response.status_code == 200

    def test_post(self):
        convention = ConventionFactory()
        url = reverse(
            "conventions:preview_upload_signed",
            kwargs={"convention_uuid": convention.uuid},
        )
        request = RequestFactory().post(
            url, data={"televersement_convention_signee_le": "09/08/2024"}
        )
        user = UserFactory(is_superuser=True)
        request.user = user
        request.session = "session"

        response = ConventionDateUploadSignedView.as_view()(
            request, convention_uuid=convention.uuid
        )

        convention.refresh_from_db()
        assert response.status_code == 302
        assert (
            response.headers["Location"]
            == "/conventions/post_action/42196b48-1cdd-4ccb-b14b-d42c38269f11"
        )
        assert convention.televersement_convention_signee_le == datetime.date(
            2024, 8, 9
        )
        assert convention.statut == "5. Signée"
