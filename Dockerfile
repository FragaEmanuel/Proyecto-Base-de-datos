# Dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p database

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Cambiar el comando para que escuche en todas las interfaces
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]