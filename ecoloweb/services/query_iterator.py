from django.db.backends.utils import CursorWrapper


class QueryResultIterator:
    """
    Iterator on rows returned by a SQL query. It computes rows count first and serves each one by one as dict.
    """

    def __init__(self, connection, query, parameters=[]):
        self._connection: CursorWrapper = connection
        # Compute result number, first
        self._connection.execute(f'select count(*) from ({query}) q', parameters)
        self.lines_total = self._connection.fetchone()[0]

        # Execute query
        self.lines_fetched = 0
        self._connection.execute(query, parameters)
        self._columns = [col[0] for col in self._connection.description]

    def __iter__(self):
        return self

    def __next__(self):
        if row := self._connection.fetchone():
            self.lines_fetched += 1

            return dict(zip(self._columns, row))

        raise StopIteration
