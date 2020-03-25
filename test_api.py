from models import Rate, peewee_datetime

from config import logging, LOGGER_CONFIG

log = logging.getLogger("TestApi")
fh = logging.FileHandler(LOGGER_CONFIG["file"])
fh.setLevel(LOGGER_CONFIG["level"])
fh.setFormatter(LOGGER_CONFIG["formatter"])
log.addHandler(fh)
log.setLevel(LOGGER_CONFIG["level"])


def update_rates(from_currency, to_currency):
    log.info(f"Started update for: {from_currency}=>{to_currency}")
    rate = Rate.select().where(Rate.from_currency == from_currency,
                               Rate.to_currency == to_currency).first()
    log.debug(f"rate before: {rate}")
    rate.rate += 0.01
    rate.updated = peewee_datetime.datetime.now()
    rate.save()

    log.debug(f"rate after: {rate}")
    log.info(f"Finished update for: {from_currency}=>{to_currency}")
