# -*- coding: utf-8 -*-
"""
    hss_app.snmp.oids
    ~~~~~~~~~~~~~~~~~

    This module defines all SNMP service OIDs
    
    :copyright: (c) 2023-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

oids = {
    "mib": "1.3.6.1.2.1",
    "sys_descr": "1.3.6.1.2.1",

    "air:num_requests": "1.0.0.0",
    "air:num_answers:success": "1.0.0.1",
    "air:num_answers:missing_avp": "1.0.0.2",
    "air:num_answers:invalid_avp_value": "1.0.0.3",
    "air:num_answers:user_unknown": "1.0.0.4",
    "air:num_answers:authentication_data_unavailable": "1.0.0.5",

    "nor:num_requests": "2.0.0.0",
    "nor:num_answers:success": "2.0.0.1",
    "nor:num_answers:missing_avp": "2.0.0.2",
    "nor:num_answers:invalid_avp_value": "2.0.0.3",
    "nor:num_answers:user_unknown": "2.0.0.4",
    "nor:num_answers:unknown_serving_node": "2.0.0.5",

    "pur:num_requests": "3.0.0.0",
    "pur:num_answers:success": "3.0.0.1",
    "pur:num_answers:missing_avp": "3.0.0.2",
    "pur:num_answers:invalid_avp_value": "3.0.0.3",
    "pur:num_answers:user_unknown": "3.0.0.4",

    "ulr:num_requests": "4.0.0.0",
    "ulr:num_answers:success": "4.0.0.1",
    "ulr:num_answers:missing_avp": "4.0.0.2",
    "ulr:num_answers:invalid_avp_value": "4.0.0.3",
    "ulr:num_answers:user_unknown": "4.0.0.4",
    "ulr:num_answers:rat_not_allowed": "4.0.0.5",
    "ulr:num_answers:realm_not_served": "4.0.0.6",
    "ulr:num_answers:roaming_not_allowed": "4.0.0.7",
    "ulr:num_answers:unknown_eps_subscription": "4.0.0.8",
}