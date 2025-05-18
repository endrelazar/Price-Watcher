# Price Watcher API

This is a FastAPI-based price watcher application that monitors the prices of specified products and sends email notifications when the price drops below a set target.

## Main Features

- Add, delete, and list products
- Automatic price updates and monitoring with a timer
- Email notifications when the product price reaches the target
- Extensible webshop support

## Installation (local run)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Using Docker

1. **Build the image:**
   ```bash
   docker build -t arertesito .
   ```

2. **Start the container:**
   ```bash
   docker run -p 8000:8000 arertesito
   ```

Or with `docker-compose`:
   ```bash
   docker-compose up --build
   ```

## Email sending setup

For email notifications, you need a `config.json` file in the project root directory containing your own email address and password (Freemail.hu account required):

```json
{
    "email_felado": "your.email@example.com",
    "email_jelszo": "your-password"
}
```

**Attention:**  
Do not upload `config.json` to a public repository, as it contains sensitive data!  
Add it to your `.gitignore`:

```
config.json
```

## Webshop extension

If you want to support a new webshop, edit the `elmfind.json` file, where you can add the necessary settings for the new webshop. This allows the system to be easily extended to additional online stores.

## Example API endpoints

- `POST /products/` – Add a new product
- `GET /products/` – List products
- `POST /update-prices/` – Update prices
- `DELETE /products/{id}` – Delete a product

## Developer information

- Python 3.10+
- FastAPI
- SQLAlchemy
- Docker support

---

**Portfolio project. For questions: github [endrelazar]**