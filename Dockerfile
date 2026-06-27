FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
COPY entrypoint.prod.sh /entrypoint.prod.sh

RUN chmod +x /entrypoint.sh /entrypoint.prod.sh

ENTRYPOINT ["/entrypoint.sh"]