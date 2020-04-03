import xml.etree.ElementTree as ET

from api import _Api

CBR_API_URL = 'http://www.cbr.ru/scripts/XML_daily.asp'


class Api(_Api):
    def __init__(self):
        super().__init__("CbrApi")

    def _update_rate(self, xrate):
        rate = self._get_cbr_rate(xrate.from_currency)
        return rate

    def _get_cbr_rate(self, from_currency):
        response = self._send_request(url=CBR_API_URL, method="GET")
        self.log.debug(f"response.encoding: {response.encoding}")
        response_text = response.text
        self.log.debug(f"response.text: {response_text}")
        rate = self._find_rate(response_text, from_currency)

        return rate

    def _find_rate(self, response_text, from_currency):
        root = ET.fromstring(response_text)
        valutes = root.findall("Valute")
        aliases_map = {840: "USD", 643: "RUB"}
        currency_alias = aliases_map[from_currency]

        for valute in valutes:
            if valute.find('CharCode').text == currency_alias:
                print(valute)
                return float(valute.find("Value").text.replace(",", "."))
        raise ValueError(f"Invalid Cbr response: {from_currency}")
