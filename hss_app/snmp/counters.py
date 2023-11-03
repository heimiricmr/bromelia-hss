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


class CounterDB(redis.Redis):
    def __init__(self, **kwargs):
        redis.Redis.__init__(self, **kwargs)

app_counterdb = CounterDB(password="eYVX7EwVmmxKPCDmwMtyKVge8oLd2t81")
