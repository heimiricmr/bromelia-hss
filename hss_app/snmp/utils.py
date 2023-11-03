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
import re
import subprocess
import socket


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


def get_default_ip_address() -> str:
    try:
        result = subprocess.run(["ip", "route", "get", "1"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            pattern = re.findall(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\suid", line)
            if pattern:
                return pattern[0]

    except Exception as e:
        print(f"Error: {e}")
        return None


def get_host_ip_address():
    if is_docker():
        return "0.0.0.0"
    return get_default_ip_address()
    

def get_cache_ip_address():
    try:
        cache_hostname = socket.gethostbyname_ex("hss_app-cache")
        print(f"Resolved hss_app-cache FQDN: {cache_hostname}")
        return "hss_app-cache"

    except socket.gaierror:
        print("Not found hss_app-cache FQDN, fallback to default ...")
        return "127.0.0.1"
