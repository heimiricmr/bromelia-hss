# -*- coding: utf-8 -*-
"""
    hss_app.snmp.utils
    ~~~~~~~~~~~~~~~~~~

    This module implements utility functions for SNMP service.
    
    :copyright: (c) 2023-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

#: Python standard libs
import os


def convert(oid):
    return tuple(int(i) for i in oid.split("."))


def convert_oids(oids):
    for key, value in oids.items():
        oids[key] = convert(value)
    return oids


def is_docker():
    path = '/proc/self/cgroup'
    return (
        os.path.exists('/.dockerenv') or
        os.path.isfile(path) and any('docker' in line for line in open(path))
    )

def get_host_ip_address():
    if is_docker():
        return "0.0.0.0"
    return "localhost"
