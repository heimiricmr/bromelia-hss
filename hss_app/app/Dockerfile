FROM python:3.9-slim

RUN useradd hss

WORKDIR /home/hss

RUN apt-get update && apt-get install -y \
  libpq-dev \
  python-dev \
  gcc \
  && rm -rf /var/lib/apt/lists/*

COPY app.py boot.sh counters.py entrypoint.py milenage.py models.py requirements.txt utils.py ./
COPY config_docker.py config.py
COPY config_docker.yaml config.yaml

RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip setuptools wheel
RUN venv/bin/pip install -r requirements.txt

RUN chmod +x boot.sh
RUN chown -R hss:hss ./
USER hss

EXPOSE 3870
ENTRYPOINT ["./boot.sh"]