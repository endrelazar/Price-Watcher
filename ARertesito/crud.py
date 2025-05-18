import logging
from sqlalchemy.orm import Session
from ARertesito.db import models
import ARertesito.schemas as schemas
from ARertesito.scraper import scrape_price
from datetime import datetime,UTC
import pytz

utc = pytz.UTC

def create_product(db: Session, product: schemas.ProductCreate):
    try:
        
        current_price = scrape_price(product.url)
        

        if current_price is None:
            logging.error(f"Hiba a termék árának lekérésekor: {product.url}")
            raise ValueError("Nem sikerült lekérni a termék árát")
            
        

        db_product = models.WatchedProduct(
            url=product.url,
            name=product.name,
            target_price=product.target_price,
            current_price=current_price,
            notify_interval_minutes=product.notify_interval_minutes,
            useremail=product.useremail,
            last_checked=datetime.now(UTC)  
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logging.info(f"Termék hozzáadva: {db_product.url} - Célár: {db_product.target_price} Ft")   
        return db_product
    except Exception as e:
        db.rollback()
        raise e

def get_all_products(db: Session):
    return db.query(models.WatchedProduct).all()

def delete_product(db: Session, product_id: int):
    product = db.query(models.WatchedProduct).filter(models.WatchedProduct.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
        logging.info(f"Termék törölve: {product.url}")
    return product