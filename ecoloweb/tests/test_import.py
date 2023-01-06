import os
from datetime import datetime
from pathlib import Path
from unittest import TestCase, skipIf

from django.db import connections, OperationalError
from django.db.backends.utils import CursorWrapper

from ecoloweb.services import ConventionImporter


class EcolowebImportTest(TestCase):

    is_ecoloweb_configured: bool = False
    _connection: CursorWrapper

    def setUp(self) -> None:
        self._check_db_connection()
        self._provision_database()

    def _check_db_connection(self):
        if "ecoloweb" in connections:
            try:
                self._connection = connections["ecoloweb"].cursor()
            except OperationalError:
                self.is_ecoloweb_configured = False
            else:
                self.is_ecoloweb_configured = True
        else:
            self.is_ecoloweb_configured = False

    def _provision_database(self):
        # TODO import these files from a S3 bucket in CircleCI https://circleci.com/developer/orbs/orb/circleci/aws-s3
        resource_dir = Path(os.path.join(os.path.dirname(__file__), "resources"))

        for file in resource_dir.iterdir():

            if str(file).endswith(".sql"):
                self._connection.execute(open(file).read())

    def test_import(self):
        # Skip test if no test database can be found
        if not self.is_ecoloweb_configured:
            self.skipTest("Ecoloweb tests skipped as no database correctly configured")

        importer = ConventionImporter("50", datetime.today())
        results = list(importer.get_all_by_departement())

        self.assertEqual(len(results), 2)
