import glob
import os
from datetime import datetime
from pathlib import Path
from unittest import TestCase

from django.db import connections
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

    def _provision_database(self):
        if self._connection is not None:
            resource_dir = Path(
                os.path.join(os.path.dirname(__file__), "resources/sql")
            )

            files = sorted(
                list(glob.iglob(str(resource_dir) + "/**/*.sql", recursive=True))
            )

            for file in files:
                # print(f" * Loading sql file {file}")
                self._connection.execute(open(file).read())

    def test_import(self):
        # Skip test if no test database can be found
        if self._connection is None:
            self.skipTest("Ecoloweb tests skipped as no database correctly configured")

        importer = ConventionImporter("33", datetime.today())
        importer.setup_db()

        instances = []
        for result in importer.get_all():
            instances.append(importer.process_result(result))

        self.assertEqual(len(instances), 11)

        importer = ConventionImporter("29", datetime.today())

        instances = []
        for result in importer.get_all():
            instances.append(importer.process_result(result))

        self.assertEqual(len(instances), 1)
