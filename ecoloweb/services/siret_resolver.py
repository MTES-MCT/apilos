from datetime import date
from typing import Optional
from api_insee import ApiInsee
from box.exceptions import BoxKeyError
from django.conf import settings
from box import Box


class SiretResolver:
    """
    Link to INSEE API doc: https://api.insee.fr/catalogue/site/themes/wso2/subthemes/insee/pages/item-info.jag?name=Sirene&version=V3&provider=insee
    """

    def __init__(self):
        self._insee_api_client = ApiInsee(
            key=settings.INSEE_API_KEY,
            secret =settings.INSEE_API_SECRET
        )
        self._box = Box(box_dots=True)

    def resolve(self, siren: str, date_creation: Optional[date] = None) -> Optional[str]:
        if len(siren) != 9 or not siren.isdigit():
            return None

        if date_creation:
            data = self._insee_api_client.siren(siren, date=date_creation.isoformat(), masquerValeursNulles=True).get()
        else:
            data = self._insee_api_client.siren(siren, masquerValeursNulles=True).get()

        # Process API JSON result with dot notation via Box
        self._box.incoming = data

        try:
            nic = self._box['incoming.uniteLegale.periodesUniteLegale.[0].nicSiegeUniteLegale']

            return siren + nic

        except BoxKeyError:
            return None
