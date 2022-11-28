import mock

from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase

from bailleurs.models import Bailleur
from conventions.services import (
    services_programmes,
    utils,
)
from core.tests import utils_fixtures
from instructeurs.models import Administration
from programmes.forms import (
    ProgrammeSelectionFromDBForm,
    ProgrammeSelectionFromZeroForm,
)
from programmes.models import Lot
from users.models import GroupProfile, User


class ConventionSelectionServiceForInstructeurTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def setUp(self):
        self.request = RequestFactory().get("/conventions/selection")
        self.request.user = User.objects.get(username="fix")
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        middleware.process_request(self.request)
        self.request.session.save()
        self.request.session["currently"] = GroupProfile.INSTRUCTEUR
        self.service = services_programmes.ConventionSeletionService(
            request=self.request
        )

    def test_get_from_db(self):
        administration = Administration.objects.get(code="75000")
        lots = (
            Lot.objects.filter(programme__administration=administration)
            .order_by(
                "programme__ville", "programme__nom", "nb_logements", "financement"
            )
            .filter(programme__parent_id__isnull=True)
        )
        self.service.get_from_db()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, ProgrammeSelectionFromDBForm)
        self.assertEqual(
            self.service.form.declared_fields["lot"].choices,
            [(lot.uuid, str(lot)) for lot in lots],
        )

    def test_post_from_db(self):
        pass

    def test_get_from_zero(self):
        administration = Administration.objects.get(code="75000")
        bailleurs = Bailleur.objects.all().order_by("nom")
        self.service.get_from_zero()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, ProgrammeSelectionFromZeroForm)
        self.assertEqual(
            self.service.form.declared_fields["administration"].choices,
            [(administration.uuid, str(administration))],
        )
        self.assertEqual(
            self.service.form.declared_fields["bailleur"].choices,
            [(bailleur.uuid, str(bailleur)) for bailleur in bailleurs],
        )

    def test_post_from_zero(self):
        pass


class ConventionSelectionServiceForBailleurTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def setUp(self):
        self.request = RequestFactory().get("/conventions/selection")
        self.request.user = User.objects.get(username="raph")
        get_response = mock.MagicMock()
        middleware = SessionMiddleware(get_response)
        middleware.process_request(self.request)
        self.request.session.save()
        self.request.session["currently"] = GroupProfile.BAILLEUR
        self.service = services_programmes.ConventionSeletionService(
            request=self.request
        )

    def test_get_from_db(self):
        bailleurs = Bailleur.objects.filter(siret__in=["987654321", "12345678901234"])
        lots = (
            Lot.objects.filter(programme__bailleur__in=bailleurs)
            .order_by(
                "programme__ville", "programme__nom", "nb_logements", "financement"
            )
            .filter(programme__parent_id__isnull=True)
        )
        print(lots)
        self.service.get_from_db()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, ProgrammeSelectionFromDBForm)
        self.assertEqual(
            self.service.form.declared_fields["lot"].choices,
            [(lot.uuid, str(lot)) for lot in lots],
        )

    def test_post_from_db(self):
        pass

    def test_get_from_zero(self):
        administrations = Administration.objects.all().order_by("nom")
        bailleurs = Bailleur.objects.filter(
            siret__in=["987654321", "12345678901234"]
        ).order_by("nom")
        self.service.get_from_zero()
        self.assertEqual(self.service.return_status, utils.ReturnStatus.ERROR)
        self.assertIsInstance(self.service.form, ProgrammeSelectionFromZeroForm)
        self.assertEqual(
            self.service.form.declared_fields["administration"].choices,
            [
                (administration.uuid, str(administration))
                for administration in administrations
            ],
        )
        self.assertEqual(
            self.service.form.declared_fields["bailleur"].choices,
            [(bailleur.uuid, str(bailleur)) for bailleur in bailleurs],
        )

    def test_post_from_zero(self):
        pass
