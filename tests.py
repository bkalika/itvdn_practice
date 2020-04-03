import unittest
import json
from unittest.mock import patch
import xml.etree.ElementTree as ET

import xmltodict
import requests

import models
import api
import test_api
# import cbr_api
# import privat_api
# from api import privat_api, cbr_api, cryptonator_api

PRIVAT_API_URL = 'https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11'
CBR_API_URL = 'http://www.cbr.ru/scripts/XML_daily.asp'
CRYPRONATOR_API_URL = 'https://api.cryptonator.com/api/ticker/'
LOCALHOST_URL = 'http://localhost:5000/api/rates/'
LOCALHOST_URL_RATES = 'http://localhost:5000/rates'


def get_privat_response(*args, **kwargs):
    print("get_privat_response")

    class Response:
        def __init__(self, response):
            self.text = json.dumps(response)

        def json(self):
            return json.loads(self.text)

    return Response([{"ccy": "USD", "base_ccy": "UAH", "sale": "30.0"}])


class Test(unittest.TestCase):
    def setUp(self):
        models.init_db()

    def test_main(self):
        rate = models.Rate.get(id=1)
        updated_before = rate.updated
        self.assertEqual(rate.rate, 1.0)
        test_api.update_rates(840, 980)
        rate = models.Rate.get(id=1)
        updated_after = rate.updated

        self.assertEqual(1.01, rate.rate)
        self.assertGreater(updated_after, updated_before)

    @unittest.skip("skip")
    def test_privat_usd(self):
        rate = models.Rate.get(id=1)
        updated_before = rate.updated
        self.assertEqual(rate.rate, 1.0)
        # privat_api.update_rates(840, 900)  # old api
        api.update_rate(840, 980)  # new api
        rate = models.Rate.get(id=1)
        updated_after = rate.updated

        self.assertGreater(rate.rate, 26)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, PRIVAT_API_URL)
        self.assertIsNotNone(api_log.response_text)

        self.assertIn('[{"ccy":"USD","base_ccy":"UAH",', api_log.response_text)

    @unittest.skip("skip")
    def test_privat_btc(self):
        # rate = models.Rate.get(from_currency=1000, to_currency=980)
        rate = models.Rate.get(id=1)
        updated_before = rate.updated
        self.assertEqual(rate.rate, 1.0)
        # privat_api.update_rates(840, 900)  # old api
        api.update_rate(1000, 840)  # new api
        rate = models.Rate.get(from_currency=1000, to_currency=840)
        updated_after = rate.updated

        self.assertGreater(rate.rate, 5000)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, PRIVAT_API_URL)

    @unittest.skip("skip")
    def test_cbr(self):
        rate = models.Rate.get(from_currency=840, to_currency=643)
        updated_before = rate.updated
        self.assertEqual(rate.rate, 1.0)
        # cbr_api.update_rates(840, 900)  # old api
        api.update_rate(840, 643)  # new api
        rate = models.Rate.get(from_currency=840, to_currency=643)
        updated_after = rate.updated

        self.assertGreater(rate.rate, 70)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()
        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, CBR_API_URL)
        self.assertIsNotNone(api_log.response_text)
        self.assertIn("<NumCode>840</NumCode>", api_log.response_text)

    @unittest.skip("skip")
    @patch('api._Api._send', new=get_privat_response)
    def test_privat_mock(self):
        rate = models.Rate.get(id=1)
        updated_before = rate.updated
        self.assertEqual(rate.rate, 1.0)

        api.update_rate(840, 980)

        rate = models.Rate.get(id=1)
        updated_after = rate.updated

        self.assertEqual(rate.rate, 28.0112)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, PRIVAT_API_URL)
        self.assertIsNotNone(api_log.response_text)
        self.assertIn('[{"ccy":"USD","base_ccy":"UAH","buy":"27.40000","sale":"28.01120"}', api_log.response_text)

    @unittest.skip("skip")
    def test_api_error(self):
        api.HTTP_TIMEOUT = 0.001
        rate = models.Rate.get(id=1)
        updated_before = rate.updated
        self.assertEqual(rate.rate, 1.0)
        self.assertRaises(requests.exceptions.RequestException, api.update_rate, 840, 980)

        rate = models.Rate.get(id=1)
        updated_after = rate.updated

        self.assertEqual(rate.rate, 1.0)
        self.assertEqual(updated_before, updated_after)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, PRIVAT_API_URL)
        self.assertIsNone(api_log.response_text)
        self.assertIsNotNone(api_log.error)

        error_log = models.ErrorLog.select().order_by(models.ErrorLog.created.desc()).first()
        self.assertIsNotNone(error_log)
        self.assertEqual(error_log.request_url, PRIVAT_API_URL)
        self.assertIsNotNone(error_log.traceback)
        self.assertEqual(api_log.error, error_log.error)
        self.assertIn("Connection to api.privatbank.ua timed out", error_log.error)

        api.HTTP_TIMEOUT = 15

    @unittest.skip("skip")
    def test_crypronator_uah(self):
        from_currency = 1000
        to_currency = 980
        xrate = models.Rate.get(from_currency=from_currency, to_currency=to_currency)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)

        api.update_rate(1000, 980)

        xrate = models.Rate.get(from_currency=from_currency, to_currency=to_currency)
        updated_after = xrate.updated

        self.assertGreater(xrate.rate, 150000)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog().select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        full_url = CRYPRONATOR_API_URL + "BTC-UAH"
        self.assertEqual(api_log.request_url, full_url)
        self.assertIsNotNone(api_log.response_text)
        self.assertIn('[{"base":"BTC","target":"UAH","price":', api_log.response_text)

    def test_xml_api(self):
        full_url = LOCALHOST_URL + "/xml"
        r = requests.get(full_url)
        self.assertIn("<rates>", r.text)
        xml_rates = xmltodict.parse(r.text)
        self.assertIn("rates", xml_rates)
        self.assertIsInstance(xml_rates["rates"]["rate"], list)
        self.assertEqual(len(xml_rates["rates"]["rate"]), 5)

    def test_json_api(self):
        full_url = LOCALHOST_URL + "json"
        r = requests.get(full_url)
        json_rates = r.json()
        self.assertIsInstance(json_rates, list)
        self.assertEqual(len(json_rates), 5)
        for rate in json_rates:
            for key_ in ["from", "to", "rate"]:
                self.assertIn(key_, rate)

    def test_json_api_uah(self):
        full_url = LOCALHOST_URL + "json?to_currency=980"
        r = requests.get(full_url)
        json_rates = r.json()
        self.assertIsInstance(json_rates, list)
        self.assertEqual(len(json_rates), 2)

    def test_html_rates(self):
        r = requests.get(LOCALHOST_URL_RATES)
        self.assertTrue(r.ok)
        # print(r.text)
        self.assertIn('<table border="1">', r.text)
        root = ET.fromstring(r.text)
        print(root)
        body = root.find("body")
        self.assertIsNotNone(body)
        table = body.find("table")
        self.assertIsNotNone(table)
        rows = table.findall("tr")
        self.assertEqual(len(rows), 5)


if __name__ == "__main__":
    unittest.main()
