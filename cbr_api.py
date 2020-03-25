import xml.etree.ElementTree as ET

import requests

from models import Rate, peewee_datetime
from config import logging, LOGGER_CONFIG

CBR_API_URL = 'http://www.cbr.ru/scripts/XML_daily.asp'

log = logging.getLogger("CbrApi")
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
    rate.rate = get_cbr_rate(from_currency)
    rate.updated = peewee_datetime.datetime.now()
    rate.save()

    log.debug(f"rate after: {rate}")
    log.info(f"Finished update for: {from_currency}=>{to_currency}")


def get_cbr_rate(from_currency):
    response = requests.get(CBR_API_URL)
    log.debug(f"response.encoding: {response.encoding}")
    response_text = response.text
    log.debug(f"response.text: {response_text}")
    usd_rate = find_usd_rate(response_text)

    return usd_rate


def find_usd_rate(response_text):
    root = ET.fromstring(response_text)
    valutes = root.findall("Valute")

    for valute in valutes:
        if valute.find("CharCode").text == "USD":
            return float(valute.find("Value").text.replace(',', '.'))

    raise ValueError("Invalid CBR response: USD not found!")
