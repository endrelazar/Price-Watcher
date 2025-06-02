FROM python:3.13-slim

WORKDIR /app

# Függőségek másolása és telepítése
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Csak Chromium böngésző telepítése Playwright-hoz
RUN pip install playwright && \
    playwright install --with-deps chromium

# Kód bemásolása
COPY . /app

# Port megnyitása
EXPOSE 8000

# Alkalmazás indítása
CMD ["uvicorn", "ARertesito.main:app", "--host", "0.0.0.0", "--port", "8000"]
