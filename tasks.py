from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from models import Rate
import api

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=1)
def update_rates():
    print(f"Job srarted at {datetime.now()}")
    rates = Rate.select()
    for rate in rates:
        try:
            api.update_rate(rate.from_currency, rate.to_currency)
        except Exception as ex:
            print(ex)
    print(f"Job finished at {datetime.now()}")


sched.start()
