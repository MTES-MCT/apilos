import os
from datetime import datetime
from pathlib import Path
from unittest import TestCase, skipIf

from django.db import connections, OperationalError
from django.db.backends.utils import CursorWrapper

from ecoloweb.services import ConventionImporter


class EcolowebImportTest(TestCase):

    is_ecoloweb_configured: bool = False
    _connection: CursorWrapper | None = None

    def setUp(self) -> None:
        self._check_db_connection()
        self._provision_database()

    def _check_db_connection(self):
        if "ecoloweb" in connections:
            self._connection = connections["ecoloweb"].cursor()
        else:
            raise OperationalError("Missing connection ecoloweb")

    def _provision_database(self):
        if self._connection is not None:
            # TODO import these files from a S3 bucket in CircleCI https://circleci.com/developer/orbs/orb/circleci/aws-s3
            resource_dir = Path(os.path.join(os.path.dirname(__file__), "resources"))

            for file in resource_dir.iterdir():

                if str(file).endswith(".sql"):
                    self._connection.execute(open(file).read())

    def test_import(self):
        # Skip test if no test database can be found
        if self._connection is None:
            self.skipTest("Ecoloweb tests skipped as no database correctly configured")

        importer = ConventionImporter("50", datetime.today())
        results = list(importer.get_all_by_departement())

        self.assertEqual(len(results), 2)
