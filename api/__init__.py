import traceback
import importlib
import requests

from config import logging, LOGGING, HTTP_TIMEOUT

from models import Rate, peewee_datetime, ErrorLog, ApiLog

# fh = logging.FileHandler(LOGGING[1]['handlers']["file"])
# print(fh)
# fh.setLevel(LOGGING["level"])
# fh.setFormatter(LOGGING["formatter"])
logging.config.dictConfig(LOGGING)


def update_rate(from_currency, to_currency):
    rate = Rate.select().where(Rate.from_currency == from_currency,
                               Rate.to_currency == to_currency).first()
    module = importlib.import_module(f"api.{rate.module}")
    module.Api().update_rate(rate)


class _Api:
    def __init__(self, logger_name):
        self.log = logging.getLogger("Api")
        self.log.name = logger_name

    def update_rate(self, rate):
        self.log.info(f"Started update for: {rate}")
        self.log.debug(f"rate before: {rate}")
        rate.rate = self._update_rate(rate)
        rate.updated = peewee_datetime.datetime.now()
        rate.save()

        self.log.debug(f"rate after: {rate}")
        self.log.info(f"Finished update for {rate}")

    def _update_rate(self, xrate):
        raise NotImplementedError("_update_rate")

    def _send_request(self, url, method, data=None, headers=None):
        log = ApiLog(request_url=url, request_data=data, request_method=method,
                     request_headers=headers)
        try:
            response = requests.request(method=method, url=url, headers=headers, data=data, timeout=15)
            log.response_text = response.text
            return response
        except Exception as ex:
            self.log.exception("Error during request sending")
            log.error = str(ex)
            ErrorLog.create(request_data=data, request_url=url, request_method=method,
                            error=str(ex), traceback=traceback.format_exc(chain=False))
            raise
        finally:
            log.finished = peewee_datetime.datetime.now()
            log.save()

    def _send(self, url, method, data=None, headers=None):
        return requests.request(method=method, url=url, headers=headers, data=data, timeout=HTTP_TIMEOUT)
