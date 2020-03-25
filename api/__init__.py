from config import logging, LOGGER_CONFIG

from models import Rate, peewee_datetime

fh = logging.FileHandler(LOGGER_CONFIG["file"])
fh.setLevel(LOGGER_CONFIG["level"])
fh.setFormatter(LOGGER_CONFIG["formatter"])


class _Api:
    def __init__(self, logger_name):
        self.log = logging.getLogger(logger_name)
        self.log.addHandler(fh)
        self.log.setLevel(LOGGER_CONFIG["level"])

    def update_rate(self, from_currency, to_currency):
        self.log.info(f"Started update for: {from_currency}=>{to_currency}")
        xrate = Rate.select().where(Rate.from_currency == from_currency,
                                    Rate.to_currency == to_currency).first()

        self.log.debug(f"rate before: {xrate}")
        xrate.rate = self._update_rate(xrate)
        xrate.updated = peewee_datetime.datetime.now()
        xrate.save()

        self.log.debug(f"rate after: {xrate}")
        self.log.info(f"Finished update for: {from_currency}=>{to_currency}")

    def _update_rate(self, xrate):
        raise NotImplementedError("_update_rate")
