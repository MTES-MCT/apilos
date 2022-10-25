from conventions.models import Convention
from .handlers import ModelImportHandler
from .handlers_bailleurs import BailleurImportHandler
from .handlers_programmes import ProgrammeImportHandler, ProgrammeLotImportHandler


class ConventionImportHandler(ModelImportHandler):
    model = Convention
    sql_template = 'resources/sql/conventions.sql'

    def _get_dependencies(self):
        return {
            'programme': ProgrammeImportHandler(),
            'lot': ProgrammeLotImportHandler(),
            'bailleur': BailleurImportHandler(),
        }

    def import_all(self, criteria: dict = None):
        if criteria is None:
            criteria = {}

        # Run query
        for data in self.query_multiple_rows(self._get_sql_query(criteria)):
            self._count += 1 if self._process_result(data) else 0

        print(f"Migrated {self._count} convention(s)")
