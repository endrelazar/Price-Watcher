
FROM python:3.13-slim
FROM mcr.microsoft.com/playwright/python:v1.52.0

WORKDIR /app

# Függőségek másolása és telepítése
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Kód bemásolása
COPY . /app

# Port megnyitása
EXPOSE 8000

# Alkalmazás indítása
CMD ["uvicorn", "ARertesito.main:app", "--host", "0.0.0.0", "--port", "8000"]
