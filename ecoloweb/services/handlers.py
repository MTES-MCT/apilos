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
    ecolo_id_field = 'id'

    def __init__(self):
        self._count: int = 0
        self._connection: CursorWrapper = connections['ecoloweb'].cursor()

    @property
    @abstractmethod
    def model(self):
        raise NotImplementedError

    @abstractmethod
    def sql_template(self):
        raise NotImplementedError

    def _get_sql_query(self, criteria: dict) -> str:
        return self._get_sql_from_template(self.sql_template, criteria)

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
            ecolo_id=str(ecolo_id),
            apilos_id=apilos_id
        )

    def _get_identity_keys(self) -> List[str]:
        """
        Return the list of fields to match an existing instance on DB, using get_or_create
        """
        return []

    def _get_dependencies(self):
        """
        Return a dict of key -> ModelImportHandler

        This will replace fields with key `key` by their related model via the call of the related
        ModelImportHandler.import_one()
        """
        return {}

    def _process_result(self, data: dict) -> Optional[Model]:
        # Enrich data by replacing dependencies references with imported instance
        for key, handler in self._get_dependencies().items():
            if f'{key}_id' in data:
                data[key] = handler.import_one(data.pop(f'{key}_id'))
            elif key in data:
                data[key] = handler.import_one(data.pop(key))

        instance = self._find_existing_model(data)
        if instance is None:
            ecolo_id = data.pop(self.ecolo_id_field)

            if len(self._get_identity_keys()) > 0:
                filters = {key: data[key] for key in self._get_identity_keys()}
                instance, created = self.model.objects.get_or_create(**filters, defaults=data)

                self._register_ecolo_reference(instance, ecolo_id)
                if created:
                    self._count += 1
            else:
                instance = self.model.objects.create(**data)
                self._register_ecolo_reference(instance, ecolo_id)
                self._count += 1

        return instance

    def _find_existing_model(self, data: dict) -> Optional[Model]:
        if self.ecolo_id_field in data:
            ref = self._find_ecolo_reference(self.model, data[self.ecolo_id_field])
            if ref is not None:
                res = ref.resolve()

                return res

        return None

    def import_one(self, pk: int) -> Optional[Model]:
        return self._process_result(
            self.query_single_row(
                self._get_sql_query({'pk': pk})
            )
        )

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
