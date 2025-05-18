from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from ARertesito.db.database import SessionLocal, engine,Base
from ARertesito.db import models
import ARertesito.crud as crud
import ARertesito.schemas as schemas
from ARertesito.scraper import scrape_price,scrape_name
from datetime import datetime
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import logging
import time
import threading
from ARertesito.notifier import check_prices_and_notify
from contextlib import asynccontextmanager
import os

#log file-ba és konzolra
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    filename="arertesito.log",
    filemode="a"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)


def background_notifier():
    while True:
        check_prices_and_notify()
        time.sleep(60)  # 1 percenként ellenőriz


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    t = threading.Thread(target=background_notifier, daemon=True)
    t.start()
    yield
    

app = FastAPI(
    title="Árfigyelő API",
    description="Ez az API lehetővé teszi termékek árának figyelését és frissítését.",
    version="1.0.0",
    lifespan=lifespan)

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

Base.metadata.create_all(bind=engine) # Adatbázis táblák létrehozása
# Dependency – lekéri az adatbázis kapcsolatot
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UpdatePricesResponse(BaseModel):
    updated: int
    products: list[schemas.ProductOut]


@app.post("/update-prices/", response_model=UpdatePricesResponse)
def update_prices(db: Session = Depends(get_db)):
    """Frissíti az összes termék árát és visszaadja a frissített termékeket."""
    products = crud.get_all_products(db)
    updated_products = []
    updated_count = 0

    for product in products:
        try:
            new_price = scrape_price(product.url)
            if new_price is not None and new_price != product.current_price:
                product.current_price = new_price
                product.last_checked = datetime.utcnow()
                db.add(product)
                db.commit()
                db.refresh(product)
                updated_products.append(product)
                updated_count += 1
                logging.info(f"Termék frissítve: {product.url} - Új ár: {new_price} Ft")
        except Exception as e:
            logging.exception(f"Hiba történt a termék frissítésekor (id={product.id}): {str(e)}")
            db.rollback()
    
    return {"updated": updated_count, "products": updated_products}


@app.get("/")
def read_root():
    return {"message": "Árfigyelő API működik"}


@app.post("/products/", response_model=schemas.ProductOut)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Új termék létrehozása és hozzáadása az adatbázishoz."""
    try:
        if not product.url:
            raise HTTPException(status_code=400, detail="Az URL mező kitöltése kötelező.")
        if product.target_price is None or product.target_price <= 0:
            raise HTTPException(status_code=400, detail="A célár mező kitöltése kötelező és nagyobbnak kell lennie nullánál.")
        if not product.useremail:  # <-- email kötelező ellenőrzése
            raise HTTPException(status_code=400, detail="Az email mező kitöltése kötelező.")
        
        # Terméknév lekérése az URL alapján 
        if not product.name:
            try:
                product.name = scrape_name(product.url)
                # Ha nem sikerült nevet lekérni, használjuk az URL-t
                if not product.name:
                    product.name = product.url
            except Exception as e:
                logging.exception(f"Hiba a név lekérésekor: {str(e)}")
                product.name = product.url
        
        # Termék létrehozása
        db_product = crud.create_product(db=db, product=product)
        return db_product

    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logging.exception(f"Hiba a termék létrehozásakor: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Szerverhiba történt a termék létrehozásakor.")


@app.get("/products/", response_model=list[schemas.ProductOut])
def read_products(db: Session = Depends(get_db)):
    """Lekéri az összes terméket az adatbázisból."""
    return crud.get_all_products(db)

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Törli a megadott terméket az adatbázisból."""
    product = db.query(models.WatchedProduct).filter(models.WatchedProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Termék nem található")
    db.delete(product)
    db.commit()
    return {"ok": True}

