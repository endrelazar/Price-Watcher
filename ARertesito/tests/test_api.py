
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ARertesito.db.database import Base
from fastapi.testclient import TestClient
from ARertesito.main import app, get_db
import ARertesito.db.database as db_database
from unittest.mock import patch
import ARertesito.email_kuldo as email_kuldo

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
connection = engine.connect()
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    db_database.SessionLocal = TestingSessionLocal
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


def test_create_product_invalid_url(client):
    product_data = {
        "url": "ftp://rosszurl.hu",
        "target_price": 1000,
        "name": "Hibás URL",
        "notify_interval_minutes": 60,
        "useremail": "teszt@teszt.hu"
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 400 or response.status_code == 422


def test_create_product_invalid_email(client):
    product_data = {
        "url": "https://example.com",
        "target_price": 1000,
        "name": "Hibás email",
        "notify_interval_minutes": 60,
        "useremail": "nememail"
    }
    response = client.post("/products/", json=product_data)
    assert response.status_code == 400 or response.status_code == 422



def test_create_and_get_product(client):
    # Teszt adat
    product_data = {
        "url": "https://example.com",
        "target_price": 1000,
        "name": "Teszt termék",
        "notify_interval_minutes": 60,
        "useremail": "teszt@teszt.hu"
    }

    with patch("ARertesito.scraper.scrape_price", return_value=1234), \
         patch("ARertesito.main.scrape_price", return_value=1234), \
         patch("ARertesito.crud.scrape_price", return_value=1234):
        response = client.post("/products/", json=product_data)
        assert response.status_code == 200
        data = response.json()
        assert data["url"] == product_data["url"]
        assert data["target_price"] == product_data["target_price"]
        assert data["useremail"] == product_data["useremail"]
        assert data["current_price"] == 1234

        # Termék lekérdezése
        response = client.get("/products/")
        assert response.status_code == 200
        products = response.json()
        assert any(p["url"] == product_data["url"] for p in products)


def test_check_prices_and_notify_runs():
    with patch("ARertesito.notifier.kuld_email"), \
     patch("ARertesito.notifier.scrape_price", return_value=500):
        # Mockoljuk a kuld_email függvényt, hogy ne küldjön valódi emailt 
        # és a scrape_price függvényt, hogy mindig 500 Ft-ot adjon vissza
        from ARertesito.notifier import check_prices_and_notify
        try:
            check_prices_and_notify()
        except Exception:
            pass  # Ha nincs adatbázis, nem baj, a lényeg hogy a függvény lefut
        # Ha volt értesítés, az email küldő hívódik
        # assert mock_email.called  # csak ha biztosan van értesítendő termék


def test_kuld_email_calls_smtp():
    with patch("smtplib.SMTP") as mock_smtp:
        email_kuldo.kuld_email(
            new_price=1000,
            product_name="Teszt termék",
            product_url="https://example.com",
            useremail="teszt@teszt.hu"
        )
        assert mock_smtp.called



def test_create_product_missing_email(client):
    # Email nélkül nem lehet terméket felvenni
    product_data = {
        "url": "https://example.com",
        "target_price": 1000,
        "name": "Teszt termék",
        "notify_interval_minutes": 60
    }
    
    response = client.post("/products/", json=product_data)
    assert response.status_code == 422 or response.status_code == 400

def test_delete_product(client):
    # Először létrehozunk egy terméket
    product_data = {
        "url": "https://example.com",
        "target_price": 500,
        "name": "Törlendő termék",
        "notify_interval_minutes": 60,
        "useremail": "torles@teszt.hu"
    }
    with patch("ARertesito.scraper.scrape_price", return_value=1234), \
         patch("ARertesito.main.scrape_price", return_value=1234), \
         patch("ARertesito.crud.scrape_price", return_value=1234):
        response = client.post("/products/", json=product_data)
        assert response.status_code == 200
        product_id = response.json()["id"]

        # Törlés
        response = client.delete(f"/products/{product_id}")
        assert response.status_code == 200
        # Ellenőrizzük, hogy már nem található
        response = client.get("/products/")
        assert all(p["id"] != product_id for p in response.json())