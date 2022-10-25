from conventions.models import Convention
from .handlers import ModelImporter
from .handlers_bailleurs import BailleurImporter
from .handlers_programmes import ProgrammeImporter, ProgrammeLotImporter


class ConventionImporter(ModelImporter):
    model = Convention
    sql_template = 'resources/sql/conventions.sql'

    def _get_dependencies(self):
        return {
            'programme': ProgrammeImporter(),
            'lot': ProgrammeLotImporter(),
            'bailleur': BailleurImporter(),
        }

    def import_all(self, criteria: dict = None):
        if criteria is None:
            criteria = {}

        # Run query
        for data in self.query_multiple_rows(self._get_sql_query(criteria)):
            self._nb_imported_models += 1 if self._process_result(data) else 0

        print(f"Migrated {self._nb_imported_models} convention(s)")
