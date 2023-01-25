from django.db import connections
from django.db.backends.utils import CursorWrapper


class QueryResultIterator:
    """
    Iterator on rows returned by a SQL query. It computes rows count first and serves each one by one as dict.
    """

    def __init__(self, query, connection: CursorWrapper | None = None, parameters=None):
        if parameters is None:
            parameters = []
        self._db_connection: CursorWrapper = (
            connection if connection is not None else connections["ecoloweb"].cursor()
        )
        # Execute query
        self.lines_fetched = 0
        self._db_connection.execute(query, parameters)
        self._columns = [col[0] for col in self._db_connection.description]
        self.lines_total = self._db_connection.rowcount

    def __iter__(self):
        return self

    def __next__(self):
        if row := self._db_connection.fetchone():
            self.lines_fetched += 1

            return dict(zip(self._columns, row))

        raise StopIteration
