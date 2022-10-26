from datetime import date
from typing import Optional
from api_insee import ApiInsee
from django.conf import settings

class SiretResolver:
    """
    Link to INSEE API doc: https://api.insee.fr/catalogue/site/themes/wso2/subthemes/insee/pages/item-info.jag?name=Sirene&version=V3&provider=insee

    """

    def __init__(self):
        self._insee_api_client = ApiInsee(
            key=settings.INSEE_API_KEY,
            secret =settings.INSEE_API_SECRET
        )

    def resolve(self, siren: str) -> Optional[str]:
        data = self._insee_api_client.siren(siren, date=date.today().isoformat(), masquerValeursNulles=True).get()

        nic = data['uniteLegale']['periodesUniteLegale'][0]['nicSiegeUniteLegale']
        if nic:
            return siren + nic

        return siren + 'XXXXX'