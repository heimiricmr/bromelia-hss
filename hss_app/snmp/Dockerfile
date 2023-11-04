FROM python:3.9-slim

RUN useradd snmp

WORKDIR /home/snmp

RUN apt-get update && apt-get install -y \
  python-dev-is-python3 \
  && rm -rf /var/lib/apt/lists/*

COPY counters.py entrypoint.py oids.py utils.py ./
COPY boot.sh requirements.txt ./

RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip setuptools wheel
RUN venv/bin/pip install -r requirements.txt

RUN chmod +x boot.sh
RUN chown -R snmp:snmp ./
USER snmp

EXPOSE 1161/udp
ENTRYPOINT ["./boot.sh"]