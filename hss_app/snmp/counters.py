# -*- coding: utf-8 -*-
"""
    hss_app.snmp.counters
    ~~~~~~~~~~~~~~~~~~~~~

    This module implements Redis connector.
    
    :copyright: (c) 2023-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

#: 3rd-party dependencies
import redis

#: project modules
from utils import get_cache_ip_address


class CounterDB(redis.Redis):
    def __init__(self, **kwargs):
        redis.Redis.__init__(self, **kwargs)

app_counterdb = CounterDB(host=get_cache_ip_address(), password="eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81", socket_connect_timeout=2)
