from api import _Api

PRIVAT_API_URL = 'https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11'


class Api(_Api):
    def __init__(self):
        super().__init__("PrivatApi")

    def _update_rate(self, xrate):
        rate = self._get_privat_rate(xrate.from_currency)
        return rate

    def _get_privat_rate(self, from_currency):
        response = self._send_request(url=PRIVAT_API_URL, method="GET")
        response_json = response.json()
        self.log.debug(f"Privat response: {response_json}")
        rate = self._find_rate(response_json, from_currency)

        return rate

    def _find_rate(self, response_data, from_currency):
        aliases_map = {840: "USD"}
        currency_alias = aliases_map[from_currency]
        for e in response_data:
            if e["ccy"] == currency_alias:
                return float(e['sale'])
        raise ValueError(f"Invalid Privat response: {currency_alias} not found.")
