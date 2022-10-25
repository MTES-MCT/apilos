from .handlers import ModelImportHandler
from bailleurs.models import Bailleur


class BailleurImportHandler(ModelImportHandler):
    model = Bailleur
    sql_template = 'resources/sql/bailleurs.sql'
