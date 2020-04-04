from functools import wraps

from flask import request, abort

from app import app
import controllers
from config import IP_LIST


def check_ip(func):
    @wraps(func)
    def checker(*args, **kwargs):
        if request.remote_addr not in IP_LIST:
            return abort(403)
        return func(*args, **kwargs)
    return checker


@app.route("/")
def hello():
    return "Hello home"


@app.route("/rates")
def view_rates():
    return controllers.ViewAllRates().call()


@app.route("/api/rates/<fmt>")
def api_rates(fmt):
    return controllers.GetApiRates().call(fmt)


@app.route("/update/<int:from_currency>/<int:to_currency>")
@app.route("/update/all")
def update_rates(from_currency=None, to_currency=None):
    return controllers.UpdateRates().call(from_currency, to_currency)


@app.route("/edit/<int:from_currency>/<int:to_currency>", methods=["GET", "POST"])
@check_ip
def edit_rate(from_currency, to_currency):
    return controllers.EditRate().call(from_currency=from_currency,
                                       to_currency=to_currency
                                       )


@app.route("/logs/<log_type>")
@check_ip
def view_logs(log_type):
    return controllers.ViewLogs().call(log_type)
