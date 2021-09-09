import datetime
from bailleurs.models import Bailleur

def create_bailleur():
    return Bailleur.objects.create(
        nom="3F",
        siret="12345678901234",
        capital_social="SA",
        ville="Marseille",
        dg_nom="Patrick Patoulachi",
        dg_fonction="PDG",
        dg_date_deliberation=datetime.date(2014, 10, 9),
    )
