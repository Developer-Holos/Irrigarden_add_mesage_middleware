FROM python:3.12-slim

WORKDIR /app

# Dependencias de sistema (OpenCV, tesseract si usas OCR):
RUN apt-get update && apt-get install -y \
    libgl1 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requisitos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar toda la app
COPY . .

# Arranca con Python, no con Uvicorn CLI
CMD ["python", "-u", "app/main.py"]