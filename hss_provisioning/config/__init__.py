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
import socket
import os


#: Dir paths
config_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(config_dir)
logging_dir = os.path.join(base_dir, "logs")


def is_docker():
    path = '/proc/self/cgroup'
    return (
        os.path.exists('/.dockerenv') or
        os.path.isfile(path) and any('docker' in line for line in open(path))
    )


def get_database_user():
    if os.getenv("POSTGRES_USER"):
        print("Found POSTGRES_USER env variable")
        return os.getenv("POSTGRES_USER")
    print("Not found POSTGRES_USER env variable, fallback to default ...")
    return "postgres"


def get_database_password():
    if os.getenv("POSTGRES_PASSWORD"):
        print("Found POSTGRES_PASSWORD env variable")
        return os.getenv("POSTGRES_PASSWORD")
    print("Not found POSTGRES_PASSWORD env variable, fallback to default ...")
    return "1234HssPostgres!"


def get_database_url():
    try:
        postgres_hostname = socket.gethostbyname_ex("hss_app-postgres")
        print("Found hss_app-postgres FQDN")
        return "hss_app-postgres:5432"

    except socket.gaierror:
        print("Not found hss_app-postgres FQDN, fallback to default ...")
        return "127.0.0.1:5432"


def get_database_db():
    if os.getenv("POSTGRES_DB"):
        print("Found POSTGRES_DB env variable")
        return os.getenv("POSTGRES_DB")
    print("Not found POSTGRES_DB env variable, fallback to default ...")
    return "subscribers"


def get_host_ip_address():
    if is_docker():
        return "0.0.0.0"
    return "localhost"


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


class Config:
    #: Network Configuration
    HOST = get_host_ip_address()
    PORT = 5001

    #: SQLAlchemy and PostgreSQL configurations
    SECRET_KEY = "you-will-never-guess"

    params = {
        "user": get_database_user(), 
        "pw": get_database_password(), 
        "url": get_database_url(), 
        "db": get_database_db()
    }

    SQL_BASE_URI = "postgresql+psycopg2://{user}:{pw}@{url}/{db}?client_encoding=utf8".format(**params)

    SQLALCHEMY_BINDS = {
        "hss": SQL_BASE_URI.format(**params),
    }

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
