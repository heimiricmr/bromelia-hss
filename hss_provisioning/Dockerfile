FROM python:3.9-slim

RUN useradd hss

WORKDIR /home/hss

COPY ./config ./config
COPY ./models ./models
COPY ./routes ./routes

COPY app.py constants.py entrypoint.py exceptions.py utils.py ./
COPY boot.sh requirements.txt ./

RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip setuptools wheel
RUN venv/bin/pip install -r requirements.txt

RUN chmod +x boot.sh
RUN chown -R hss:hss ./
USER hss

EXPOSE 5001
ENTRYPOINT ["./boot.sh"]