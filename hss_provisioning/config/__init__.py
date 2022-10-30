# -*- coding: utf-8 -*-
"""
    hss_provisioning.config
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module contains Bromelia-HSS Provisioning app's configuration
    structures.

    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

import datetime
import json
import logging
import os


#: Dir paths
config_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(config_dir)
logging_dir = os.path.join(base_dir, "logs")

#: SQLAlchemy and PostgreSQL configurations
SECRET_KEY = "you-will-never-guess"
db = {
        "user": "postgres",
        "pw": "1234HssPostgres!", 
        "url": "localhost:5432",
        "db": "subscribers"
}

SQL_BASE_URI = "postgresql+psycopg2://{user}:{pw}@{url}/{db}?client_encoding=utf8".format(**db)

SQLALCHEMY_BINDS = {
    "hss": SQL_BASE_URI.format(**db),
}


def get_logging_filename():
    now = datetime.datetime.now()

    year = str(now.year).zfill(2)
    month = str(now.month).zfill(2)
    day = str(now.day).zfill(2)

    hour = str(now.hour).zfill(2)
    minute = str(now.minute).zfill(2)
    second = str(now.second).zfill(2)

    return f"log-hss_provisioning-{year}-{month}-{day}-{hour}-"\
           f"{minute}-{second}-UTC3-pid_{os.getpid()}.log"


def get_json_repr(filepath):
    with open(filepath, encoding="utf-8") as json_file:
        return json.load(json_file)


#: JSON API Schema - Request & Response.
request_schema_subscriber = get_json_repr(
    os.path.join(config_dir, "api_request_subscriber.json")
)

response_schema_subscriber = get_json_repr(
    os.path.join(config_dir, "api_response_subscriber.json")
)

request_schema_apn = get_json_repr(
    os.path.join(config_dir, "api_request_apn.json")
)


#: Logging setup.
logging_filename = get_logging_filename()

LOGGING_LEVEL = logging.DEBUG

LOGGING_FORMAT = "%(asctime)s [%(levelname)s] [%(process)d] "\
                "[%(thread)d:%(threadName)s] %(module)s [%(name)s] "\
                "[%(funcName)s]: %(message)s"

if not os.path.exists(logging_dir):
    os.mkdir(logging_dir)

LOGGING_PATH = os.path.join(logging_dir, f"{logging_filename}")

logging.basicConfig(level=LOGGING_LEVEL,
                    format=LOGGING_FORMAT,
                    filename=LOGGING_PATH,
                    filemode="a")
