import os

from typing import Optional, List, Dict
from abc import ABC, abstractmethod

from django.db import connections
from django.db.backends.utils import CursorWrapper
from django.db.models import Model
from django.template import Template, Context
from django.utils import timezone

from ecoloweb.models import EcoloReference


class ModelImportHandler(ABC):

    def __init__(self):
        self._count: int = 0
        self._connection: CursorWrapper = connections['ecoloweb'].cursor()

    @abstractmethod
    def _get_sql_query(self, criteria: dict) -> str:
        pass

    def _get_file_content(self, path):
        return ''.join(open(os.path.join(os.path.dirname(__file__), path), 'r').readlines())

    def _get_sql_from_template(self, path: str, context: dict = {}):
        return Template(self._get_file_content(path)) \
            .render(Context(context | {'timezone': timezone.get_current_timezone()}))

    def _get_sql_from_file(self, path: str) -> str:
        return self._get_file_content(path)

    def _find_ecolo_reference(self, clazz, ecolo_id: int) -> Optional[EcoloReference]:
        return EcoloReference.objects.filter(
            apilos_model=EcoloReference.get_class_model_name(clazz),
            ecolo_id=ecolo_id
        ).first()

    def _resolve_reference(self, clazz, ecolo_id: int) -> Optional[Model]:
        if ref := self._find_ecolo_reference(clazz, ecolo_id) is None:
            return None

        return ref.resolve()

    def _register_ecolo_reference(self, instance: Model, ecolo_id: int, id: Optional[int] = None):
        apilos_id = id if id is not None else instance.id

        EcoloReference.objects.create(
            apilos_model=EcoloReference.get_instance_model_name(instance),
            ecolo_id=ecolo_id,
            apilos_id=apilos_id
        )

    @abstractmethod
    def _process_data(self, data: dict) -> Optional[Model]:
        pass

    def import_one(self, pk: int) -> Optional[Model]:
        return None

    def import_all(self, criteria: dict = None):
        if criteria is None:
            criteria = {}
        count: int = 0

        # Run query
        for data in self.query_multiple_rows(self._get_sql_query(criteria)):
            self._count += 1 if self._process_data(data) else 0

        self.on_complete()

    def on_complete(self):
        pass

    def query_single_row(self, query: str) -> Optional[Dict]:
        self._connection.execute(query)

        columns = [col[0] for col in self._connection.description]
        row = self._connection.fetchone()

        return dict(zip(columns, row)) if row else None

    def query_multiple_rows(self, query: str) -> List[Dict]:
        self._connection.execute(query)

        columns = [col[0] for col in self._connection.description]

        return list(map(lambda row: dict(zip(columns, row)), self._connection.fetchall()))
