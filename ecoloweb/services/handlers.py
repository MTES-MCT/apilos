import os

from typing import Optional

from abc import ABC, abstractmethod
from django.db.backends.utils import CursorWrapper
from django.db.models import Model
from django.template import Template, Context
from django.utils import timezone

from ecoloweb.models import EcoloReference


class ModelImportHandler(ABC):
    connection: CursorWrapper
    count: int = 0

    def __init__(self, connection: CursorWrapper):
        self.connection = connection

    @abstractmethod
    def _get_sql_query(self) -> str:
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
    def _process_row(self, data: dict) -> bool:
        pass

    def handle(self):
        count: int = 0

        # Run query
        self.connection.execute(self._get_sql_query())
        # Extract metadata to be able to convert each row into a dict
        columns = [col[0] for col in self.connection.description]

        # To reduce memory allocation we fetch rows 1 by 1
        while (row := self.connection.fetchone()) is not None:
            data = dict(zip(columns, row))
            self.count += 1 if self._process_row(data) else 0

        self.on_complete()

    def on_complete(self):
        pass
