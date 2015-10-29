__author__ = 'Nhan Trinh'

from django_cron import CronJobBase, Schedule
from .models import *
from datetime import datetime

class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 60 * 24
    RETRY_AFTER_FAILURE_MINS = 1
    RUN_AT_TIME = ['11:59']

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS,retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS, run_at_times=RUN_AT_TIME)
    code = 'yyas_web.my_cron_job'    # a unique code

    def do(self):
        Auction.batch_resolve()


