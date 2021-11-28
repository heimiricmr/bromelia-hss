# -*- coding: utf-8 -*-
"""
    hss_app.config
    ~~~~~~~~~~~~~~

    This module contains configuration structures.

    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""
import os

basedir = os.path.dirname(os.path.abspath(__file__))

#: Database URI
user = os.environ["POSTGRES_USER"] = "postgres"
pwd = os.environ["POSTGRES_PASSWORD"] = "1234HssPostgres!"

server_hostname = "localhost"
server_port = "5432"
database_name = os.environ["POSTGRES_DB"] = "subscribers"

database_uri = f"postgresql://{user}:{pwd}@{server_hostname}:{server_port}/{database_name}"

#: Bromelia Config File (CEX procedure)
config_file = os.path.join(basedir, "config.yaml")
