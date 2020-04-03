from datetime import datetime

from flask import render_template, make_response, request, jsonify, redirect, url_for
import xmltodict

from models import Rate, ApiLog
import api

# def get_all_rates():
#     try:
#         rates = Rate.select()
#         return render_template("rates.html", rates=rates)
#     except Exception as ex:
#         return make_response(str(ex), 500)


class BaseController:
    def __init__(self):
        self.request = request

    def call(self, *args, **kwargs):
        try:
            return self._call(*args, **kwargs)
        except Exception as ex:
            return make_response(str(ex), 500)

    def _call(self, *args, **kwargs):
        raise NotImplementedError("_call")


class ViewAllRates(BaseController):
    def _call(self):
        rates = Rate.select()
        return render_template("rates.html", rates=rates)


class GetApiRates(BaseController):
    def _call(self, fmt):
        rates = Rate.select()
        rates = self._filter(rates)

        if fmt == "json":
            return self._get_json(rates)
        elif fmt == "xml":
            return self._get_xml(rates)
        raise ValueError(f"Unknown fmt: {fmt}")

    def _filter(self, rates):
        args = self.request.args

        if "from_currency" in args:
            rates = rates.where(Rate.from_currency == args.get("from_currency"))
        if "to_currency" in args:
            rates = rates.where(Rate.to_currency == args.get("to_currency"))

        return rates

    def _get_xml(self, rates):
        d = {"rates": {"rate": [
            {"from": rate.from_currency,
             "to": rate.to_currency,
             "rate": rate.rate} for rate in rates
        ]}}
        return make_response(xmltodict.unparse(d), {"Content-Type": "text/xml"})

    def _get_json(self, rates):
        return jsonify([{"from": rate.from_currency,
                         "to": rate.to_currency,
                         "rate": rate.rate} for rate in rates])


class UpdateRates(BaseController):
    def _call(self, from_currency, to_currency):
        if not from_currency and not to_currency:
            self._update_all()

        elif from_currency and to_currency:
            self._update_rate(from_currency, to_currency)

        else:
            raise ValueError("from_currency and to_currency")
        return redirect("/rates")

    def _update_rate(self, from_currency, to_currency):
        api.update_rate(from_currency, to_currency)

    def _update_all(self):
         rates = Rate.select()
         for rate in rates:
             try:
                 self._update_rate(rate.from_currency, rate.to_currency)
             except Exception as ex:
                 print(ex)


class ViewLogs(BaseController):
    def _call(self):
        page = int(self.request.args.get("page", 1))
        logs = ApiLog.select().paginate(page, 10).order_by(ApiLog.id.desc())
        return render_template("logs.html", logs=logs)


class EditRate(BaseController):
    def _call(self, from_currency, to_currency):
        if self.request.method == "GET":
            return render_template("edit_rate.html", from_currency=from_currency, to_currency=to_currency)

        print(request.form)
        if "new_rate" not in request.form:
            raise Exception("new_rate parameter is required")

        if not request.form["new_rate"]:
            raise Exception("new_rate must be not empty")

        upd_count = (Rate.update({Rate.rate: float(request.form["new_rate"]),
                                  Rate.updated: datetime.now()})).where(Rate.from_currency == from_currency,
                                                                        Rate.to_currency == to_currency).execute()
        print("upd_count", upd_count)
        return redirect(url_for('view_rates'))
