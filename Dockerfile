FROM python:3.12-slim

WORKDIR /app

# Instala dependencias del sistema para OpenCV
RUN apt-get update && apt-get install -y libgl1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"