# -*- coding: utf-8 -*-
"""
    hss_app.snmp.generate
    ~~~~~~~~~~~~~~~~~~~~~

    This module implements a generator which creates an entrypoint.py module
    based on oids.py module entries
    
    :copyright: (c) 2023-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

#: Python standard libs
import os
import re

#: project modules
from oids import oids

base_dir = os.path.dirname(os.path.abspath(__file__))
hss_app_dir = os.path.dirname(base_dir)

app_dir = os.path.join(hss_app_dir, "app")


def create_header():
    return f'''# -*- coding: utf-8 -*-
"""
    hss_app.snmp.entrypoint
    ~~~~~~~~~~~~~~~~~~~~~~~

    The central entrypoint to run SNMP service.
    
    :copyright: (c) 2023-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

#: 3rd-party dependencies
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity import config, engine
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.proto.api import v2c

#: project modules
from counters import app_counterdb
from oids import oids
from utils import convert_oids, get_host_ip_address


snmpEngine = engine.SnmpEngine()

oids = convert_oids(oids)

## UDP over IPv4
config.addTransport(
    snmpEngine,
    udp.domainName,
    udp.UdpTransport().openServerMode((get_host_ip_address(), 1161))
)

## SNMPv3/USM setup

# user: usr-md5-none, auth: MD5, priv NONE
config.addV3User(
    snmpEngine, 'usr-md5-none',
    config.usmHMACMD5AuthProtocol, 'authkey1'
)

# Allow full MIB access for each user at VACM
config.addVacmUser(snmpEngine, 3, 'usr-md5-none', 'authNoPriv', oids.get("mib"), oids.get("mib"))

## SNMPv2c setup

# SecurityName <-> CommunityName mapping.
config.addV1System(snmpEngine, 'bromelia-hss', 'public')

# Allow full MIB access for this user / securityModels at VACM
config.addVacmUser(snmpEngine, 2, 'bromelia-hss', 'noAuthNoPriv', oids.get("mib"), oids.get("mib"))

# Get default SNMP context this SNMP engine serves
snmpContext = context.SnmpContext(snmpEngine)

# Create an SNMP context with default ContextEngineId (same as SNMP engine ID)
snmpContext = context.SnmpContext(snmpEngine)
mibBuilder = snmpContext.getMibInstrum().getMibBuilder()

MibScalar, MibScalarInstance = mibBuilder.importSymbols(
    'SNMPv2-SMI', 'MibScalar', 'MibScalarInstance'
)
    '''

def create_footer():
    return f'''
# Register SNMP Applications at the SNMP engine for particular SNMP context
cmdrsp.GetCommandResponder(snmpEngine, snmpContext)
cmdrsp.SetCommandResponder(snmpEngine, snmpContext)
cmdrsp.NextCommandResponder(snmpEngine, snmpContext)
cmdrsp.BulkCommandResponder(snmpEngine, snmpContext)


if __name__ == "__main__":
    # Register an imaginary never-ending job to keep I/O dispatcher running forever
    snmpEngine.transportDispatcher.jobStarted(0.5)

    # Run I/O dispatcher which would receive queries and send responses
    try:
        snmpEngine.transportDispatcher.runDispatcher()

    except:
        snmpEngine.transportDispatcher.closeDispatcher()
        raise
    '''


def normalize_word(word):
    norm_word = ""
    words = [w.capitalize() for w in word.split("_")]
    for w in words:
        norm_word += w
    return norm_word


def get_class_name(key):
    class_name = ""
    for level in key.split(":"):
        class_name += f"{normalize_word(level)}_"
    return class_name[:-1]


def create_python_class(key):
    return f'''
# OID {oids.get(key)}
class {get_class_name(key)}(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('{key}'))
        except:
            return self.getSyntax().clone(0)

    '''

def create_mib_builder(keys):
    base = f"""
mibBuilder.exportSymbols(
    '__HSS_MIBS', 
    MibScalar(
                oids.get("sys_descr"), 
                v2c.OctetString()
    ),
    """

    mibs = ""

    for index, key in enumerate(keys):
        if index == len(keys) - 1:
            mibs += f"""{get_class_name(key)}(oids.get("sys_descr"), oids.get("{key}"), v2c.Integer32())\r\n)"""
        else:
            mibs += f'''{get_class_name(key)}(oids.get("sys_descr"), oids.get("{key}"), v2c.Integer32()),\r\n    '''

    return base + mibs


with open(os.path.join(base_dir, "entrypoint.py"), "w") as entrypoint_file:
    with open(os.path.join(app_dir, "app.py"), "r") as app_file:
        lines = app_file.readlines()
        keys = list()

        for line in lines:
            pattern = re.findall(r'app\_counterdb\.incr\(\"(.*)\"\)', line)
            if pattern:
                keys.append(pattern[0])

        keys = list(set(keys))
        keys.sort()

        entrypoint_file.write(create_header())

        for key in keys:
            entrypoint_file.write(create_python_class(key))
    
        entrypoint_file.write(create_mib_builder(keys))

        entrypoint_file.write(create_footer())
