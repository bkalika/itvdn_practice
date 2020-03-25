import unittest

import models
import test_api
# import cbr_api
# import privat_api
from api import privat_api, cbr_api


class Test(unittest.TestCase):
    def setUp(self):
        models.init_db()

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

        self.assertGreater(rate.rate, 25)
        self.assertGreater(updated_after, updated_before)

    def test_cbr(self):
        rate = models.Rate.get(from_currency=840, to_currency=900)
        updated_before = rate.updated
        self.assertEqual(rate.rate, 1.0)
        # cbr_api.update_rates(840, 900)  # old api
        cbr_api.Api().update_rate(840, 900)  # new api
        rate = models.Rate.get(from_currency=840, to_currency=900)
        updated_after = rate.updated

        self.assertGreater(rate.rate, 77)
        self.assertGreater(updated_after, updated_before)


if __name__ == "__main__":
    unittest.main()
