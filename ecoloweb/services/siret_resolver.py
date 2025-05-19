from datetime import date

# Cette librairie n'est plus maintenue, elle est retirée des requirements
# Je laisse ce code comme documentation de la reprise ecoloweb
# from api_insee import ApiInsee
from box import Box
from box.exceptions import BoxKeyError


class SiretResolver:
    """
    Link to INSEE API doc: https://api.insee.fr/catalogue/site/themes/wso2/subthemes/insee/pages/item-info.jag?name=Sirene&version=V3&provider=insee
    """

    def __init__(self, api_key: str, api_secret: str):
        # self._insee_api_client = ApiInsee(key=api_key, secret=api_secret)
        self._box = Box(box_dots=True)

    def resolve(self, siren: str, date_creation: date | None = None) -> str | None:
        if not siren or len(siren) != 9 or not siren.isdigit():
            return None

        if date_creation:
            data = self._insee_api_client.siren(
                siren, date=date_creation.isoformat(), masquerValeursNulles=True
            ).get()
        else:
            data = self._insee_api_client.siren(siren, masquerValeursNulles=True).get()

        # Process API JSON result with dot notation via Box
        self._box.incoming = data

        try:
            nic = self._box[
                "incoming.uniteLegale.periodesUniteLegale.[0].nicSiegeUniteLegale"
            ]

            return siren + nic

        except BoxKeyError:
            return None
