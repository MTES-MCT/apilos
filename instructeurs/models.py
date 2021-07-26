import uuid

from django.db import models
from core.models import IngestableModel

class Administration(IngestableModel):

    pivot= 'code'
    mapping= {
        'nom': 'Gestionnaire',
        'code': 'Gestionnaire (code)',
    }

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
