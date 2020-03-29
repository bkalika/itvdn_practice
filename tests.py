import json
import unittest

from unittest.mock import patch

import requests

import api
import models
import test_api
# import cbr_api
# import privat_api
from api import privat_api, cbr_api

PRIVAT_API_URL = 'https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11'
CBR_API_URL = 'http://www.cbr.ru/scripts/XML_daily.asp'


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

    # not used
    def test_main(self):
        rate = models.Rate.get(id=1)
        updated_before = rate.updated
        self.assertEqual(rate.rate, 1.0)
        test_api.update_rates(840, 900)
        rate = models.Rate.get(id=1)
        updated_after = rate.updated

        self.assertEqual(1.01, rate.rate)
        self.assertGreater(updated_after, updated_before)

    def test_privat(self):
        rate = models.Rate.get(id=1)
        updated_before = rate.updated
        self.assertEqual(rate.rate, 1.0)
        # privat_api.update_rates(840, 900)  # old api
        privat_api.Api().update_rate(840, 900)  # new api
        rate = models.Rate.get(id=1)
        updated_after = rate.updated

        self.assertGreater(rate.rate, 26)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, PRIVAT_API_URL)
        self.assertIsNotNone(api_log.response_text)

        self.assertIn('[{"ccy":"USD","base_ccy":"UAH",', api_log.response_text)

    def test_cbr(self):
        rate = models.Rate.get(from_currency=840, to_currency=643)
        updated_before = rate.updated
        self.assertEqual(rate.rate, 1.0)
        # cbr_api.update_rates(840, 900)  # old api
        cbr_api.Api().update_rate(840, 643)  # new api
        rate = models.Rate.get(from_currency=840, to_currency=643)
        updated_after = rate.updated

        self.assertGreater(rate.rate, 70)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()
        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, CBR_API_URL)
        self.assertIsNotNone(api_log.response_text)
        self.assertIn("<NumCode>840</NumCode>", api_log.response_text)

    @patch('api._Api._send', new=get_privat_response)
    def test_privat_mock(self):
        rate = models.Rate.get(id=1)
        updated_before = rate.updated
        self.assertEqual(rate.rate, 1.0)

        privat_api.Api().update_rate(840, 900)

        rate = models.Rate.get(id=1)
        updated_after = rate.updated

        self.assertEqual(rate.rate, 30)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, PRIVAT_API_URL)
        self.assertIsNotNone(api_log.response_text)
        self.assertEqual('[{"ccy": "USD", "base_ccy": "UAH", "sale": "30.0"}]', api_log.response_text)

    def test_api_error(self):
        api.HTTP_TIMEOUT = 0.001
        rate = models.Rate.get(id=1)
        updated_before = rate.updated
        self.assertEqual(rate.rate, 1.0)
        self.assertRaises(requests.exceptions.RequestException, privat_api.Api().update_rate, 840, 900)

        rate = models.Rate.get(id=1)
        updated_after = rate.updated
        self.assertEqual(rate.rate, 1.0)
        self.assertEqual(updated_after, updated_before)

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


if __name__ == "__main__":
    unittest.main()
