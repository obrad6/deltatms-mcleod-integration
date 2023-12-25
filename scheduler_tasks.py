import os
from apscheduler.schedulers.background import BackgroundScheduler
from utils import LOCKFILE
from import_orders import get_new_loads


def initialize_scheduler():
    """Initialize app scheduler."""
    if os.path.exists(LOCKFILE):
        print("Scheduler already initialized by another process.")
        return
    open(LOCKFILE, 'a').close()

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(get_new_loads, 'interval', args=[False], minutes=10)
    scheduler.start()
    print("Scheduler started.")
