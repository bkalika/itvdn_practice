import requests
from api import _Api

PRIVAT_API_URL = 'https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11'


class Api(_Api):
    def __init__(self):
        super().__init__("PrivatApi")

    def _update_rate(self, xrate):
        rate = self._get_privat_rate(xrate.from_currency)
        return rate

    def _get_privat_rate(self, from_currency):
        response = requests.get(PRIVAT_API_URL)
        self.log.debug(f"response.encoding: {response.encoding}")
        response_data = response.json()
        self.log.debug(f"response.text: {response_data}")
        rate = self._find_rate(response_data, from_currency)

        return rate

    def _find_rate(self, response_data, from_currency):
        for e in response_data:
            if e["ccy"] == "USD":
                return float(e['sale'])
        raise ValueError("Invalid Privat response: {from_currency} not found")
