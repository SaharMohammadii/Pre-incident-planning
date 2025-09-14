# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    gdal-bin libgdal-dev \
    libgeos-dev \
    libproj-dev proj-data proj-bin \
    libpq-dev \
    locales-all \
 && rm -rf /var/lib/apt/lists/*

ENV LANG=fa_IR.UTF-8 \
    LC_ALL=fa_IR.UTF-8

WORKDIR /app

COPY . /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && pip install "GDAL==$(gdal-config --version)" \
 && pip install gunicorn whitenoise

RUN useradd -m appuser

COPY entrypoint.sh /app/entrypoint.sh

RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
CMD ["/app/entrypoint.sh"]
