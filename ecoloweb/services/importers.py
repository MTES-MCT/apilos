import os
import re
import time
from datetime import date

from typing import Dict, Type
from abc import ABC, abstractmethod

from django.db import connections
from django.db.backends.utils import CursorWrapper
from django.db.models import Model
from django.template import Context, Engine
from django.utils import timezone

from ecoloweb.models import EcoloReference
from ecoloweb.services.query_iterator import QueryResultIterator


class ModelImporter(ABC):
    """
    Base importer service class whose responsibility is to ensure imports of entities from Ecoloweb
    database of a single model.

    It relies on a SQL query to fetch and hydrate new models, with some extra layers like Ecolo
    references or identity fields to avoid duplicate imports.

    Thus, if one Ecolo entity has already been imported, changes that may have
    occurred in the meantime in the Ecolo database won't be echoed to the APiLos database /!\
    """

    ecolo_id_field: str = "id"

    def __init__(
        self,
        departement: str,
        import_date: date,
        update: bool = False,
        debug=False,
    ):
        self._nb_imported_models: int = 0
        self._db_connection: CursorWrapper = connections["ecoloweb"].cursor()
        self.update = update
        self.debug = debug
        self.departement = departement
        self.import_date = import_date
        self.engine = Engine(
            dirs=[os.path.join(os.path.dirname(__file__), "resources/sql")]
        )

        self._query_one = None
        self._query_many = None

        self._identity_keys = []

    @property
    @abstractmethod
    def model(self):
        """
        The model class manipulated by the importer to make find, get_or_create or create calls.

        Abstract property that must be overriden in children classes.
        """
        raise NotImplementedError

    def _debug(self, message: str):
        if self.debug:
            print(message)

    def _get_file_content(self, path):
        """
        Simple primitive method to extract file content as string.
        """
        return "".join(
            [
                re.sub("--.*", "", line)
                for line in open(
                    os.path.join(os.path.dirname(__file__), "resources/sql", path),
                    "r",
                    encoding="utf8",
                ).readlines()
            ]
        )

    def _get_sql_from_template(self, path: str, context=None):
        """
        Generate SQL query from a Django template file, using the input `context` dictionary
        """
        if context is None:
            context = {}
        return self.engine.render_to_string(
            path, Context(context | {"timezone": timezone.get_current_timezone()})
        )

    def _rounded_value(self, value):
        return round(float(value), 2) if value is not None else None

    def find_ecolo_reference(
        self, ecolo_id: str, model: Type[Model] | None = None
    ) -> EcoloReference | None:
        """
        Based on input data, attempts to extract an existing EcoloReference, using the
        `ecolo_id_field` defined as attribute and, if found, resolve it. See EcoloReference
        class model definition to understand how it works.

        The external reference in the Ecoloweb database is a string, as sometimes there is
        no other choice than to use a hashed value (like `md5` for Programme Lots for
        example).
        """
        return EcoloReference.objects.filter(
            apilos_model=EcoloReference.get_class_model_name(
                model if model is not None else self.model
            ),
            ecolo_id=ecolo_id,
        ).first()

    def resolve_ecolo_reference(self, ecolo_id: str, model: Type[Model]) -> Model:
        """
        Find the EcoloReference of model type model with id ecolo_id in Ecolo DB
        """
        self._debug(f"Looking for ref of {model.__name__} with id {ecolo_id}")
        ecolo_reference = EcoloReference.objects.get(
            apilos_model=EcoloReference.get_class_model_name(model),
            ecolo_id=ecolo_id,
        )

        return ecolo_reference.resolve()

    def _register_ecolo_reference(
        self, instance: Model, ecolo_id: int, apilos_id: int | None = None
    ):
        """
        Create and save an EcoloReference model to mark an entity from the Ecoloweb
        database as imported
        """
        EcoloReference.objects.create(
            apilos_model=EcoloReference.get_instance_model_name(instance),
            ecolo_id=str(ecolo_id),
            apilos_id=apilos_id if apilos_id is not None else instance.id,
            departement=self.departement,
            importe_le=self.import_date,
        )

    def _get_matching_fields(self, data: dict) -> dict:
        if len(self._identity_keys) > 0:
            return {
                key: data[key]
                for key in self._identity_keys
                if key in data and data[key] is not None and data[key] != ""
            }

        return {}

    def _find_existing_model(self, data: dict) -> Model | None:
        # Extract dict values from declared identity keys as filters dict
        filters = self._get_matching_fields(data)

        return self.model.objects.filter(**filters).first()

    def _prepare_data(self, data: dict) -> dict:
        """
        Prepare data dict before it's used to create a new instance. This is
        where you can add, remove or update an attribute
        """
        return data

    def process_result(self, data: dict | None) -> Model | None:
        """
        For each result row from the base SQL query, process it by following
        these steps:
        1. look for an already imported model and if found return it
        2. if some identity fields are declared in  `_identity_keys`, attempt to
        find a matching model from the APiLos database
        3. if still no model can be found, let's create it
        4. mark the newly created model as imported to avoid duplicate imports
        """
        if data is None:
            return None

        self._debug(f"Processing result {data} for handler {self.__class__.__name__}")

        # Extraction de l'identifiant du modèle dans la base Ecolo
        ecolo_id = data.pop(self.ecolo_id_field)

        # Préparation des valeurs pour enregistrement (avec résolution récursive
        # des modèles liés dans la base Apilos)
        data = self._prepare_data(data)

        # Recherche d'une instance déjà existante dans la base Apilos selon les
        # critères d'unicité (cf. champs _identity_keys)
        existing = self._find_existing_model(data)

        # Recherche d'une éventuelle référence existante vers ce modèle issue
        # d'un précédent import
        ecolo_ref = (
            self.find_ecolo_reference(ecolo_id) if ecolo_id is not None else None
        )

        created = True

        # Si le modèle n'a encore jamais été importé depuis Ecolo ...
        if ecolo_ref is None:
            # ... et qu'aucun modèle ne correspond dans la base Apilos ...
            if existing is not None:
                # ... alors on associe l'entité existante
                instance = existing
                created = False
            # ... mais qu'un modèle correspond dans la base Apilos ...
            else:
                # ... alors on le crée
                instance = self.model.objects.create(**data)
            # On enregistre l'entité Apilos comme associé à la base Ecolo
            self._register_ecolo_reference(instance, ecolo_id)
            self._nb_imported_models += 1
        # Si le modèle a déjà été importé depuis Ecolo avant ...
        else:
            created = False
            instance = ecolo_ref.resolve()
            # ... mais que le modèle Apilos a été supprimé depuis ...
            if instance is None:
                # ... alors on marque la référence comme "supprimée"
                ecolo_ref.marquer_supprime()
                instance = None
            # ... mais qu'il existe une entité correspondante dans la base
            # Apilos ET une référence
            elif existing:
                # ... alors on met à jour la référence Ecolo avec le bon modèle
                ecolo_ref.apilos_id = existing.id
                ecolo_ref.save(update_fields=["apilos_id"])
            # ... et que la référence existe toujours ...
            elif self.update:
                # ... alors si l'import est en mode "update" on met à jour le
                # modèle cible averc les données issues d'Ecoloweb
                ecolo_ref.update(data)

        self._on_processed(ecolo_id, instance, created)

        return instance

    def _on_processed(self, ecolo_id: str | None, model: Model | None, created: bool):
        pass

    def build_query_parameters(self, pk) -> list:
        return [pk]

    def import_one(self, pk: str | int | None) -> Model | None:
        """
        Public entry point method to fetch a model from the Ecoloweb database
        based on its primary key
        """
        if pk is None:
            return None

        ecolo_ref = self.find_ecolo_reference(pk)
        existing = ecolo_ref.resolve() if ecolo_ref is not None else None

        # Si une référence vers un objet Ecolo est trouvée
        if ecolo_ref is not None:
            # Si celle-ci a été marquée comme supprimée depuis alors rien
            if ecolo_ref.est_supprime:
                return None
            # Si l'objet cible a été supprimé depuis alors on marque la
            # référence comme supprimée
            if existing is None:
                ecolo_ref.marquer_supprime()
                return None
            # Si pas en mode update alors on retourne l'instance cible
            if not self.update:
                return existing

        # Dans tous les autres cas on effectue la requête vers Ecolo
        return self.process_result(
            self._query_single_row(self.build_query_parameters(pk))
        )

    def _query_single_row(self, parameters) -> Dict | None:
        """
        Execute a SQL query returning a single result, as dict
        """
        if self._query_one is None:
            raise NotImplementedError

        start = time.time()
        self._debug(
            f"Start query for handler {self.__class__.__name__} with parameters"
            f"{parameters}"
        )
        self._db_connection.execute(self._query_one, parameters)
        stop = time.time()
        self._debug(f"End query for handler {self.__class__.__name__} ({stop - start})")

        columns = [col[0] for col in self._db_connection.description]
        row = self._db_connection.fetchone()

        return dict(zip(columns, row)) if row else None

    def import_many(self, ecolo_id: str | None):
        """
        Public entry point method to fetch a list of models from the Ecoloweb
        database based on its foreign key
        """
        if self._query_many is None:
            raise NotImplementedError

        if ecolo_id is not None:
            iterator = QueryResultIterator(
                self._query_many,
                self._db_connection,
                self.build_query_parameters(ecolo_id),
            )

            for result in iterator:
                self.process_result(result)
