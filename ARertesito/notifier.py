from ARertesito.db.database import SessionLocal
from ARertesito.scraper import scrape_price
from ARertesito.db.models import WatchedProduct
from datetime import datetime, UTC,timedelta,timezone
from ARertesito.email_kuldo import kuld_email
import logging

def check_prices_and_notify():
    db = SessionLocal()
    products = db.query(WatchedProduct).all()
    now = datetime.now(UTC)
    for product in products:
    # Ha last_checked nem None, alakítsd át offset-aware-re
        last_checked = product.last_checked
        if last_checked is not None and last_checked.tzinfo is None:
            last_checked = last_checked.replace(tzinfo=timezone.utc)
        # Ugyanez last_notified-re
        last_notified = product.last_notified
        if last_notified is not None and last_notified.tzinfo is None:
            last_notified = last_notified.replace(tzinfo=timezone.utc)

        if (not last_checked or
            now - last_checked >= timedelta(minutes=product.notify_interval_minutes)):
            new_price = scrape_price(product.url)
            if new_price is not None:
                notify = False
            if new_price <= product.target_price:
                if (not last_notified or
                    now - last_notified >= timedelta(minutes=product.notify_interval_minutes)):
                    notify = True
            if notify:
                logging.info(f"💸 Ár alá esett: {product.url}")
                logging.info(f"👉 Jelenlegi ár: {new_price} Ft | Célár: {product.target_price} Ft")
                kuld_email(new_price,product.name,product.url,product.useremail)
                product.last_notified = now
            product.current_price = new_price
            product.last_checked = now
            db.add(product)
            db.commit()

if __name__ == "__main__":
    check_prices_and_notify()
