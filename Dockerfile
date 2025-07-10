FROM python:3.12-slim

WORKDIR /app

# Dependencias de sistema
RUN apt-get update && apt-get install -y \
    libgl1 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Instala los requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código
COPY . .

# Arranca tu FastAPI con Python -m
CMD ["python", "-u", "-m", "app.main"]