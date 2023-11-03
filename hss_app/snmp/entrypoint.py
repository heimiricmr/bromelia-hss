# -*- coding: utf-8 -*-
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
    
# OID 1.0.0.5
class Air_NumAnswers_AuthenticationDataUnavailable(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('air:num_answers:authentication_data_unavailable'))
        except:
            return self.getSyntax().clone(0)

    
# OID 1.0.0.3
class Air_NumAnswers_InvalidAvpValue(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('air:num_answers:invalid_avp_value'))
        except:
            return self.getSyntax().clone(0)

    
# OID 1.0.0.2
class Air_NumAnswers_MissingAvp(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('air:num_answers:missing_avp'))
        except:
            return self.getSyntax().clone(0)

    
# OID 1.0.0.1
class Air_NumAnswers_Success(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('air:num_answers:success'))
        except:
            return self.getSyntax().clone(0)

    
# OID 1.0.0.4
class Air_NumAnswers_UserUnknown(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('air:num_answers:user_unknown'))
        except:
            return self.getSyntax().clone(0)

    
# OID 1.0.0.0
class Air_NumRequests(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('air:num_requests'))
        except:
            return self.getSyntax().clone(0)

    
# OID 2.0.0.3
class Nor_NumAnswers_InvalidAvpValue(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('nor:num_answers:invalid_avp_value'))
        except:
            return self.getSyntax().clone(0)

    
# OID 2.0.0.2
class Nor_NumAnswers_MissingAvp(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('nor:num_answers:missing_avp'))
        except:
            return self.getSyntax().clone(0)

    
# OID 2.0.0.1
class Nor_NumAnswers_Success(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('nor:num_answers:success'))
        except:
            return self.getSyntax().clone(0)

    
# OID 2.0.0.5
class Nor_NumAnswers_UnknownServingNode(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('nor:num_answers:unknown_serving_node'))
        except:
            return self.getSyntax().clone(0)

    
# OID 2.0.0.4
class Nor_NumAnswers_UserUnknown(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('nor:num_answers:user_unknown'))
        except:
            return self.getSyntax().clone(0)

    
# OID 2.0.0.0
class Nor_NumRequests(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('nor:num_requests'))
        except:
            return self.getSyntax().clone(0)

    
# OID 3.0.0.3
class Pur_NumAnswers_InvalidAvpValue(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('pur:num_answers:invalid_avp_value'))
        except:
            return self.getSyntax().clone(0)

    
# OID 3.0.0.2
class Pur_NumAnswers_MissingAvp(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('pur:num_answers:missing_avp'))
        except:
            return self.getSyntax().clone(0)

    
# OID 3.0.0.1
class Pur_NumAnswers_Success(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('pur:num_answers:success'))
        except:
            return self.getSyntax().clone(0)

    
# OID 3.0.0.4
class Pur_NumAnswers_UserUnknown(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('pur:num_answers:user_unknown'))
        except:
            return self.getSyntax().clone(0)

    
# OID 3.0.0.0
class Pur_NumRequests(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('pur:num_requests'))
        except:
            return self.getSyntax().clone(0)

    
# OID 4.0.0.3
class Ulr_NumAnswers_InvalidAvpValue(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('ulr:num_answers:invalid_avp_value'))
        except:
            return self.getSyntax().clone(0)

    
# OID 4.0.0.2
class Ulr_NumAnswers_MissingAvp(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('ulr:num_answers:missing_avp'))
        except:
            return self.getSyntax().clone(0)

    
# OID 4.0.0.5
class Ulr_NumAnswers_RatNotAllowed(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('ulr:num_answers:rat_not_allowed'))
        except:
            return self.getSyntax().clone(0)

    
# OID 4.0.0.6
class Ulr_NumAnswers_RealmNotServed(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('ulr:num_answers:realm_not_served'))
        except:
            return self.getSyntax().clone(0)

    
# OID 4.0.0.7
class Ulr_NumAnswers_RoamingNotAllowed(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('ulr:num_answers:roaming_not_allowed'))
        except:
            return self.getSyntax().clone(0)

    
# OID 4.0.0.1
class Ulr_NumAnswers_Success(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('ulr:num_answers:success'))
        except:
            return self.getSyntax().clone(0)

    
# OID 4.0.0.8
class Ulr_NumAnswers_UnknownEpsSubscription(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('ulr:num_answers:unknown_eps_subscription'))
        except:
            return self.getSyntax().clone(0)

    
# OID 4.0.0.4
class Ulr_NumAnswers_UserUnknown(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('ulr:num_answers:user_unknown'))
        except:
            return self.getSyntax().clone(0)

    
# OID 4.0.0.0
class Ulr_NumRequests(MibScalarInstance):
    def getValue(self, name, idx):
        try:
            return self.getSyntax().clone(app_counterdb.get('ulr:num_requests'))
        except:
            return self.getSyntax().clone(0)

    
mibBuilder.exportSymbols(
    '__HSS_MIBS', 
    MibScalar(
                oids.get("sys_descr"), 
                v2c.OctetString()
    ),
    Air_NumAnswers_AuthenticationDataUnavailable(oids.get("sys_descr"), oids.get("air:num_answers:authentication_data_unavailable"), v2c.Integer32()),
    Air_NumAnswers_InvalidAvpValue(oids.get("sys_descr"), oids.get("air:num_answers:invalid_avp_value"), v2c.Integer32()),
    Air_NumAnswers_MissingAvp(oids.get("sys_descr"), oids.get("air:num_answers:missing_avp"), v2c.Integer32()),
    Air_NumAnswers_Success(oids.get("sys_descr"), oids.get("air:num_answers:success"), v2c.Integer32()),
    Air_NumAnswers_UserUnknown(oids.get("sys_descr"), oids.get("air:num_answers:user_unknown"), v2c.Integer32()),
    Air_NumRequests(oids.get("sys_descr"), oids.get("air:num_requests"), v2c.Integer32()),
    Nor_NumAnswers_InvalidAvpValue(oids.get("sys_descr"), oids.get("nor:num_answers:invalid_avp_value"), v2c.Integer32()),
    Nor_NumAnswers_MissingAvp(oids.get("sys_descr"), oids.get("nor:num_answers:missing_avp"), v2c.Integer32()),
    Nor_NumAnswers_Success(oids.get("sys_descr"), oids.get("nor:num_answers:success"), v2c.Integer32()),
    Nor_NumAnswers_UnknownServingNode(oids.get("sys_descr"), oids.get("nor:num_answers:unknown_serving_node"), v2c.Integer32()),
    Nor_NumAnswers_UserUnknown(oids.get("sys_descr"), oids.get("nor:num_answers:user_unknown"), v2c.Integer32()),
    Nor_NumRequests(oids.get("sys_descr"), oids.get("nor:num_requests"), v2c.Integer32()),
    Pur_NumAnswers_InvalidAvpValue(oids.get("sys_descr"), oids.get("pur:num_answers:invalid_avp_value"), v2c.Integer32()),
    Pur_NumAnswers_MissingAvp(oids.get("sys_descr"), oids.get("pur:num_answers:missing_avp"), v2c.Integer32()),
    Pur_NumAnswers_Success(oids.get("sys_descr"), oids.get("pur:num_answers:success"), v2c.Integer32()),
    Pur_NumAnswers_UserUnknown(oids.get("sys_descr"), oids.get("pur:num_answers:user_unknown"), v2c.Integer32()),
    Pur_NumRequests(oids.get("sys_descr"), oids.get("pur:num_requests"), v2c.Integer32()),
    Ulr_NumAnswers_InvalidAvpValue(oids.get("sys_descr"), oids.get("ulr:num_answers:invalid_avp_value"), v2c.Integer32()),
    Ulr_NumAnswers_MissingAvp(oids.get("sys_descr"), oids.get("ulr:num_answers:missing_avp"), v2c.Integer32()),
    Ulr_NumAnswers_RatNotAllowed(oids.get("sys_descr"), oids.get("ulr:num_answers:rat_not_allowed"), v2c.Integer32()),
    Ulr_NumAnswers_RealmNotServed(oids.get("sys_descr"), oids.get("ulr:num_answers:realm_not_served"), v2c.Integer32()),
    Ulr_NumAnswers_RoamingNotAllowed(oids.get("sys_descr"), oids.get("ulr:num_answers:roaming_not_allowed"), v2c.Integer32()),
    Ulr_NumAnswers_Success(oids.get("sys_descr"), oids.get("ulr:num_answers:success"), v2c.Integer32()),
    Ulr_NumAnswers_UnknownEpsSubscription(oids.get("sys_descr"), oids.get("ulr:num_answers:unknown_eps_subscription"), v2c.Integer32()),
    Ulr_NumAnswers_UserUnknown(oids.get("sys_descr"), oids.get("ulr:num_answers:user_unknown"), v2c.Integer32()),
    Ulr_NumRequests(oids.get("sys_descr"), oids.get("ulr:num_requests"), v2c.Integer32())
)
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
    