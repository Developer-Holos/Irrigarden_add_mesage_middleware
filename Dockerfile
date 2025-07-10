FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libgl1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Aquí ya no dependemos de shell expansion
CMD ["python", "-u", "app/main.py"]