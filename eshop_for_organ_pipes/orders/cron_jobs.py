import datetime

from django_cron import CronJobBase, Schedule

from .nordigen import make_paid_bank_transfers


class MyCronJob(CronJobBase):
    RUN_EVERY_SECS = 1                                          # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_SECS)
    code = 'orders.cron_jobs.MyCronJob'                         # a unique code

    def do(self):
        make_paid_bank_transfers()
