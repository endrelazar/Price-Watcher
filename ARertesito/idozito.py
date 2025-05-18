import schedule
import time
from ARertesito.notifier import check_prices_once
import logging

# Időzítés
schedule.every(1).hours.do(check_prices_once)


logging.info("Árfigyelő elindítva...")

while True:
    schedule.run_pending()
    time.sleep(1)

