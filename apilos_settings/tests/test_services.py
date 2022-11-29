import os

from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse

from apilos_settings.services import BailleurListingProcessor, ImportBailleurUsersService
from bailleurs.models import Bailleur
from conventions.services.utils import ReturnStatus
from core.tests import utils_fixtures
from users.models import User


class BailleurListingProcessorTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def test_process_listing(self):
        bailleur = Bailleur.objects.get(nom='HLM')

        with open(os.path.join(os.path.dirname(__file__), './resources/listing_bailleur_ok.xlsx'), 'rb') as listing_file:
            processor = BailleurListingProcessor(filename=listing_file)
            users = processor.process()
            self.assertListEqual(users, [
                {
                    'first_name': "Jean",
                    'last_name': "Bailleur",
                    'bailleur': bailleur,
                    'email': "jean.bailleur2@apilos.com",
                    'username': "jean.bailleur2",
                },
                {
                    'first_name': "Jeanne",
                    'last_name': "Bailleur",
                    'bailleur': bailleur,
                    'email': "jeanne.bailleur@apilos.com",
                    'username': "jeanne.bailleur",
                },
                {
                    'first_name': "Chantal",
                    'last_name': "Bailleur",
                    'bailleur': bailleur,
                    'email': "chantal.bailleur@apilos.com",
                    'username': "chantal.bailleur",
                }
            ])


class ImportBailleurUsersServiceTest(TestCase):
    _request_factory = RequestFactory()
    _path = reverse('settings:import_bailleur_users')

    @classmethod
    def setUpTestData(cls):
        utils_fixtures.create_all()

    def _create_request(self, request):
        # Workaround to mock session & flash messages support (see https://stackoverflow.com/a/12011907/4558679 )
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        # Disable CSRF checking
        request._dont_enforce_csrf_checks = True

        return request

    def _get(self, path: str, data='') -> HttpRequest:
        return self._create_request(
            self._request_factory.get(path, data)
        )

    def _post(self, path: str, data=None) -> HttpRequest:
        return self._create_request(
            self._request_factory.post(path, data)
        )

    def test_get(self):
        users_count = User.objects.count()

        service = ImportBailleurUsersService(self._get(self._path))
        status = service.get()

        self.assertEqual(status, ReturnStatus.SUCCESS)
        # No user should have been created
        self.assertEqual(User.objects.count(), users_count)

    def test_upload(self):
        users_count = User.objects.count()

        with open(os.path.join(os.path.dirname(__file__), './resources/listing_bailleur_ok.xlsx'), 'rb') as listing_file:
            service = ImportBailleurUsersService(
                self._post(
                    self._path,
                    {
                        'file': listing_file,
                        'Upload': True,
                    }
                )
            )
            status = service.save()
            self.assertEqual(status, ReturnStatus.SUCCESS)
            # No user should have been created
            self.assertEqual(User.objects.count(), users_count)

    def test_submit_ok(self):
        users_count = User.objects.count()
        bailleur = Bailleur.objects.get(nom='HLM')

        service = ImportBailleurUsersService(
            self._post(
                self._path,
                {
                    "form-TOTAL_FORMS": 3,
                    "form-INITIAL_FORMS": 3,
                    "form-0-first_name": "Jean",
                    "form-0-last_name": "Bailleur",
                    "form-0-username": "jean.bailleur2",
                    "form-0-bailleur": bailleur.id,
                    "form-0-email": "jean.bailleur2@apilos.com",
                    "form-1-first_name": "Jeanne",
                    "form-1-last_name": "Bailleur",
                    "form-1-username": "jeanne.bailleur",
                    "form-1-bailleur": bailleur.id,
                    "form-1-email": "jeanne.bailleur@apilos.com",
                    "form-2-first_name": "Chantal",
                    "form-2-last_name": "Bailleur",
                    "form-2-username": "chantal.bailleur",
                    "form-2-bailleur": bailleur.id,
                    "form-2-email": "chantal.bailleur@apilos.com"
                }
            )
        )
        status = service.save()
        self.assertFalse(service.is_upload)
        self.assertEqual(status, ReturnStatus.SUCCESS)

        # No user should have been created
        self.assertEqual(User.objects.count() - users_count, 3)

        user = User.objects.filter(email='jeanne.bailleur@apilos.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, "Jeanne")
        self.assertEqual(user.last_name, "Bailleur")
        self.assertTrue(user.is_bailleur(bailleur_id=bailleur.id))
        self.assertEqual(user.username, 'jeanne.bailleur')

        user = User.objects.filter(email='jean.bailleur2@apilos.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, "Jean")
        self.assertEqual(user.last_name, "Bailleur")
        self.assertTrue(user.is_bailleur(bailleur_id=bailleur.id))
        self.assertEqual(user.username, 'jean.bailleur2')

        user = User.objects.filter(email='chantal.bailleur@apilos.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, "Chantal")
        self.assertEqual(user.last_name, "Bailleur")
        self.assertTrue(user.is_bailleur(bailleur_id=bailleur.id))
        self.assertEqual(user.username, 'chantal.bailleur')

    def test_submit_ko(self):
        users_count = User.objects.count()
        bailleur = Bailleur.objects.get(nom='HLM')

        service = ImportBailleurUsersService(
            self._post(
                self._path,
                {
                    "form-TOTAL_FORMS": 1,
                    "form-INITIAL_FORMS": 1,
                    "form-0-first_name": "Sabine",
                    "form-0-last_name": "L'autre",
                    "form-0-bailleur": bailleur.id,
                    "form-0-email": "sabine@apilos.com"
                }
            )
        )
        status = service.save()
        self.assertEqual(status, ReturnStatus.ERROR)

        # No user should have been created
        self.assertEqual(User.objects.count(), users_count)
