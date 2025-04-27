FROM python:3.10-slim

ENV FLASK_APP wiseekr.py
ENV FLASK_ENV production

# Systemabhängigkeiten für C-Extensions (z.B. netifaces) und SSL
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      gcc \
      python3-dev \
      libffi-dev \
      libssl-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY api api
COPY scripts scripts
COPY scans scans
COPY oui oui

COPY migrations migrations
COPY alembic.ini alembic.ini
COPY wiseekr.py config.py boot.sh ./

EXPOSE 5000
CMD ./boot.sh
