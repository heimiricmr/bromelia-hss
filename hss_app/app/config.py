# -*- coding: utf-8 -*-
"""
    hss_app.config
    ~~~~~~~~~~~~~~

    This module contains configuration structures.

    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

import os
import socket

basedir = os.path.dirname(os.path.abspath(__file__))


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
        print(f"Resolved hss_app-postgres FQDN: {postgres_hostname}")
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


def get_cache_ip_address():
    try:
        cache_hostname = socket.gethostbyname_ex("hss_app-cache")
        print(f"Resolved hss_app-cache FQDN: {cache_hostname}")
        return "hss_app-cache"

    except socket.gaierror:
        print("Not found hss_app-cache FQDN, fallback to default ...")
        return "127.0.0.1"


class Config:
    #: Network Configuration
    HOST = get_host_ip_address()
    PORT = 5001

    #: SQLAlchemy and PostgreSQL configurations
    SECRET_KEY = "you-will-never-guess"

    #: Database URI
    params = {
        "user": get_database_user(), 
        "pw": get_database_password(), 
        "url": get_database_url(), 
        "db": get_database_db()
    }

    SQL_BASE_URI = "postgresql+psycopg2://{user}:{pw}@{url}/{db}?client_encoding=utf8".format(**params)

    #: Cache address
    cache_ip_address = get_cache_ip_address()

    #: Bromelia Config File (CEX procedure)
    config_file = os.path.join(basedir, "config.yaml")
