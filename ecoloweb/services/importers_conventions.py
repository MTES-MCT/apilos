from conventions.models import Convention
from .importers import ModelImporter
from .importers_programmes import ProgrammeImporter, ProgrammeLotImporter, ProgrammeImporterSimple
from .query_iterator import QueryResultIterator


class ConventionImporter(ModelImporter):
    model = Convention

    def _get_sql_one_query(self) -> str:
        # No base query as conventions are never requested individually
        return ''

    def _get_o2o_dependencies(self):
        return {
            'programme': ProgrammeImporter,
            'lot': ProgrammeLotImporter,
        }

    def get_all_by_departement(self) -> QueryResultIterator:
        return QueryResultIterator(
            self._db_connection,
            self._get_file_content('resources/sql/conventions.sql'),
            [self.departement]
        )
