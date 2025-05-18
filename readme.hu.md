# Árfigyelő API

Ez egy FastAPI alapú árfigyelő alkalmazás, amely figyeli a megadott termékek árait, és emailben értesít, ha az ár egy megadott célár alá csökken.

## Fő funkciók

- Termékek hozzáadása, törlése, listázása
- Árak automatikus frissítése és figyelése időzítő beállításával
- Email értesítés, ha a termék ára eléri a célárat
- Bővíthető webshop támogatás

## Telepítés (helyi futtatás)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Docker használata

1. **Image építése:**
   ```bash
   docker build -t arertesito .
   ```

2. **Konténer indítása:**
   ```bash
   docker run -p 8000:8000 arertesito
   ```

Vagy `docker-compose`-szal:
   ```bash
   docker-compose up --build
   ```

## Email küldés beállítása

Az email értesítéshez szükséges egy `config.json` fájl a projekt gyökerében, amely tartalmazza a saját email címedet és jelszavadat (Freemail account szükséges hozzá):

```json
{
    "email_felado": "sajat.email@pelda.hu",
    "email_jelszo": "sajat-jelszo"
}
```

**Figyelem:**  
A `config.json`-t ne töltsd fel nyilvános repository-ba, mert érzékeny adatokat tartalmaz!  
Tedd bele a `.gitignore`-ba:

```
config.json
```

## Webshop bővítés

Ha új webshopot szeretnél támogatni, szerkeszd az `elmfind.json` fájlt, amelyben megadhatod az új webshophoz szükséges beállításokat. Ez lehetővé teszi a rendszer egyszerű bővítését további webáruházakra.

## Példa API végpontok

- `POST /products/` – Új termék hozzáadása
- `GET /products/` – Termékek listázása
- `POST /update-prices/` – Árak frissítése
- `DELETE /products/{id}` – Termék törlése

## Fejlesztői információk

- Python 3.10+
- FastAPI
- SQLAlchemy
- Docker támogatás

---

**Portfólió projekt. Kérdés esetén: github [endrelazar]**
                                   