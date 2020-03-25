import requests

from models import Rate, peewee_datetime

from config import logging, LOGGER_CONFIG

PRIVAT_API_URL = 'https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11'

log = logging.getLogger("PrivatApi")
fh = logging.FileHandler(LOGGER_CONFIG['file'])
fh.setLevel(LOGGER_CONFIG['level'])
fh.setFormatter(LOGGER_CONFIG['formatter'])
log.addHandler(fh)
log.setLevel(LOGGER_CONFIG['level'])


def update_rates(from_currency, to_currency):
    log.info(f"Started update for: {from_currency}=>{to_currency}")
    rate = Rate.select().where(Rate.from_currency == from_currency,
                               Rate.to_currency == to_currency).first()
    log.debug(f'rate before: {rate}')
    rate.rate = get_privat_rate(rate)
    rate.updated = peewee_datetime.datetime.now()
    rate.save()

    log.debug(f"rate after: {rate}")
    log.info(f"Finished update for: {from_currency}=>{to_currency}")


def get_privat_rate(from_currency):
    response = requests.get(PRIVAT_API_URL)
    response_json = response.json()
    log.debug(f'Privat response: {response_json}')
    usd_rate = find_usd_rate(response_json)
    return usd_rate


def find_usd_rate(response_data):
    for e in response_data:
        if e['ccy'] == "USD":
            return float(e['sale'])
    raise ValueError("Invalid Privat response: USD not found")
