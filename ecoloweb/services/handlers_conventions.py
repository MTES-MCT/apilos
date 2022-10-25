from conventions.models import Convention
from .handlers import ModelImporter
from .handlers_bailleurs import BailleurImporter
from .handlers_programmes import ProgrammeImporter, ProgrammeLotImporter
from .query_iterator import QueryResultIterator


class ConventionImporter(ModelImporter):
    model = Convention
    sql_template = 'resources/sql/conventions.sql'

    def _get_dependencies(self):
        return {
            'programme': ProgrammeImporter(),
            'lot': ProgrammeLotImporter(),
            'bailleur': BailleurImporter(),
        }

    def get_all_results(self, criteria: dict = None) -> QueryResultIterator:
        return QueryResultIterator(self._db_connection, self._get_sql_query(criteria))
