import os

from typing import Optional, List, Dict

from abc import ABC, abstractmethod
from django.db.models import Model
from django.template import Template, Context
from django.utils import timezone

from ecoloweb.models import EcoloReference


class ModelImportHandler(ABC):
    count: int = 0

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
    def _process_data(self, data: dict, importer: 'EcolowebImportService') -> Optional[Model]:
        pass

    def import_one(self, pk: int, importer: 'EcolowebImportService') -> Optional[Model]:
        return None

    def import_all(self, importer: 'EcolowebImportService', criteria: dict = None):
        if criteria is None:
            criteria = {}
        count: int = 0

        # Run query
        for data in self.query_multiple_rows(self._get_sql_query(criteria), importer):
            self.count += 1 if self._process_data(importer, data) else 0

        self.on_complete()

    def on_complete(self):
        pass

    @staticmethod
    def query_single_row(query: str, importer: 'EcolowebImportService') -> Optional[Dict]:
        importer.connection.execute(query)

        columns = [col[0] for col in importer.connection.description]
        row = importer.connection.fetchone()
        print(row)

        return dict(zip(columns, row)) if row else None

    @staticmethod
    def query_multiple_rows(query: str, importer) -> List[Dict]:
        importer.connection.execute(query)

        columns = [col[0] for col in importer.connection.description]

        return list(map(lambda row: dict(zip(columns, row)), importer.connection.fetchall()))
