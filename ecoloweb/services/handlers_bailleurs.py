from .handlers import ModelImporter
from bailleurs.models import Bailleur


class BailleurImporter(ModelImporter):
    model = Bailleur
    sql_template = 'resources/sql/bailleurs.sql'
