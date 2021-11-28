# -*- coding: utf-8 -*-
"""
    hss_app.utils
    ~~~~~~~~~~~~~

    This module implements utility functions.
    
    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

import re
import time

from bromelia._internal_utils import convert_to_6_bytes
from bromelia._internal_utils import convert_to_integer_from_bytes
from bromelia.avps import *
from bromelia.base import DiameterAVP
from bromelia.base import DiameterRequest
from bromelia.constants import *
from bromelia.exceptions import DiameterMissingAvp
from bromelia.exceptions import DiameterInvalidAvpValue
from bromelia.lib.etsi_3gpp_s6a import *

from milenage import *
from models import Apn
from models import Subscriber
from models import Mip6


pdn_types = {
                "IPv4": PDN_TYPE_IPV4, 
                "IPv6": PDN_TYPE_IPV6, 
                "IPv4v6": PDN_TYPE_IPV4V6,
                "IPv4orv6": PDN_TYPE_IPV4_OR_IPV6
}

qcis = {
            1: QCI_1, 
            2: QCI_2, 
            3: QCI_3,
            4: QCI_4,
            5: QCI_5,
            6: QCI_6,
            7: QCI_7,
            8: QCI_8,
            9: QCI_9,
            65: QCI_65,
            66: QCI_66,
            69: QCI_69,
            70: QCI_70
}

schars = {
        1: bytes.fromhex("30313030"),       # 0x0100
        2: bytes.fromhex("30323030"),       # 0x0200
        3: bytes.fromhex("30333030"),       # 0x0300
        4: bytes.fromhex("30343030"),       # 0x0400
        5: bytes.fromhex("30353030"),       # 0x0500
        6: bytes.fromhex("30363030"),       # 0x0600
        7: bytes.fromhex("30373030"),       # 0x0700
        8: bytes.fromhex("30383030"),       # 0x0800
        9: bytes.fromhex("30393030"),       # 0x0900
        10: bytes.fromhex("30613030"),      # 0x0a00
        11: bytes.fromhex("30623030"),      # 0x0b00
        12: bytes.fromhex("30633030"),      # 0x0c00
        13: bytes.fromhex("30643030"),      # 0x0d00
        14: bytes.fromhex("30653030"),      # 0x0e00
        15: bytes.fromhex("30663030"),      # 0x0f00
}


def get_imsi(request: DiameterRequest) -> str:
    if not request.has_avp("user_name_avp"):
        raise DiameterMissingAvp("User-Name AVP not found")

    if len(request.user_name_avp.data) != 15:
        raise DiameterInvalidAvpValue("User-Name AVP has invalid value")

    return request.user_name_avp.data.decode("utf-8")


def get_visited_plmn(request: DiameterRequest) -> bytes:
    if not request.has_avp("visited_plmn_id_avp"):
        raise DiameterMissingAvp("Visited-PLMN-Id AVP not found")

    return request.visited_plmn_id_avp.data


def get_num_of_requested_vectors(request: DiameterRequest) -> int:
    if not request.has_avp("requested_eutran_authentication_info_avp"):
        raise DiameterMissingAvp("Requested-EUTRAN-Authentication-Info AVP "\
                                 "not found")

    req_auth_info_avp = request.requested_eutran_authentication_info_avp

    if not req_auth_info_avp.has_avp("number_of_requested_vectors_avp"):
        raise DiameterMissingAvp("Number-Of-Requested-Vectors AVP not found")

    num_of_requested_vectors = req_auth_info_avp\
                                .number_of_requested_vectors_avp.data

    return int.from_bytes(num_of_requested_vectors, byteorder="big")


def get_immediate_response_preferred(request: DiameterRequest) -> int:
    if not request.has_avp("requested_eutran_authentication_info_avp"):
        raise DiameterMissingAvp("Requested-EUTRAN-Authentication-Info AVP "\
                                 "not found")

    req_auth_info_avp = request.requested_eutran_authentication_info_avp

    if not req_auth_info_avp.has_avp("immediate_response_preferred_avp"):
        return None

    res_preferred = req_auth_info_avp.immediate_response_preferred_avp.data
    return int.from_bytes(res_preferred, byteorder="big")


"REVIEW SQN CALCULATION"
def generate_vectors(num_of_vectors: int, key: bytes, opc: bytes, amf: bytes, sqn: bytes, plmn: bytes) -> tuple[list, bytes]:
    sqn_int = convert_to_integer_from_bytes(sqn)

    vectors = list()
    for _ in range(num_of_vectors):
        sqn = convert_to_6_bytes(sqn_int + int(time.time()/10000000))
        vector = calculate_eutran_vector(key, opc, amf, sqn, plmn)
        vectors.append(vector)

    return vectors, sqn


def generate_authentication_info_avp_data(vectors: list) -> list:
    use_index = True
    if len(vectors) < 2:
        use_index = False

    eutran_vector_avps = list()
    for index, vector in enumerate(vectors, 1):
        eutran_vector_avp = generate_eutran_vector_avp(index, vector, use_index=use_index)
        eutran_vector_avps.append(eutran_vector_avp)
    
    return eutran_vector_avps


def is_resync_required(request: DiameterRequest) -> bool:
    if not request.has_avp("requested_eutran_authentication_info_avp"):
        raise DiameterMissingAvp("Requested-EUTRAN-Authentication-Info AVP "\
                                 "not found")

    req_auth_info_avp = request.requested_eutran_authentication_info_avp

    if not req_auth_info_avp.has_avp("re_synchronization_info_avp"):
        return False

    return True


"REVIEW"
def get_resync_data(request: DiameterRequest) -> tuple[bytes, bytes]:
    if not request.has_avp("requested_eutran_authentication_info_avp"):
        raise DiameterMissingAvp("Requested-EUTRAN-Authentication-Info AVP "\
                                 "not found")

    req_auth_info_avp = request.requested_eutran_authentication_info_avp

    if not req_auth_info_avp.has_avp("re_synchronization_info_avp"):
        raise DiameterMissingAvp("Re-Synchronization-Info AVP not found")

    resync_data = req_auth_info_avp.re_synchronization_info_avp.data

    rand = resync_data[:16]     # :32
    auts = resync_data[16:]     # 32:

    return rand, auts


def is_ue_srvcc_supported(request: DiameterRequest) -> bool:
    if not request.has_avp("ue_srvcc_capability_avp"):
        return

    if request.ue_srvcc_capability_avp.data == UE_SRVCC_SUPPORTED:
        return True

    if request.ue_srvcc_capability_avp.data == UE_SRVCC_NOT_SUPPORTED:
        return False


def create_experimental_result_data(code: bytes) -> list:
    return [
            ExperimentalResultCodeAVP(code), 
            VendorIdAVP(VENDOR_ID_3GPP)
    ]


def generate_eutran_vector_avp(index: int, vector: Vector, use_index: bool = True) -> EUtranVectorAVP:
    if use_index:
        return EUtranVectorAVP([
                                    ItemNumberAVP(index),
                                    RandAVP(vector.rand),
                                    XresAVP(vector.xres),
                                    AutnAVP(vector.autn),
                                    KasmeAVP(vector.kasme)
        ])

    return EUtranVectorAVP([
                                RandAVP(vector.rand),
                                XresAVP(vector.xres),
                                AutnAVP(vector.autn),
                                KasmeAVP(vector.kasme)
    ])


def get_pdn_type(pdn_type: str) -> bytes:
    if pdn_type not in pdn_types.keys():
        raise ValueError("Invalid PDN-Type value")

    return pdn_types.get(pdn_type)


def get_qci(qci: int) -> bytes:
    if qci not in qcis.keys():
        raise ValueError("Invalid QCI value")

    return qcis.get(qci)


def create_apn_configuration_avp(apn: Apn, mip6: Mip6) -> ApnConfigurationAVP:
    pdn_type = get_pdn_type(apn.pdn_type)
    qci = get_qci(apn.qci)

    if mip6.destination_realm is None and \
       mip6.destination_host is None:

        return ApnConfigurationAVP([
                                        ContextIdentifierAVP(apn.apn_id),
                                        ServiceSelectionAVP(apn.apn_name),
                                        PdnTypeAVP(pdn_type),
                                        EpsSubscribedQosProfileAVP([
                                                            QosClassIdentifierAVP(qci),
                                                            AllocationRetentionPriorityAVP([PriorityLevelAVP(apn.priority_level)])
                                        ]),
                                        AmbrAVP([
                                            MaxRequestedBandwidthDlAVP(apn.max_req_bw_dl),
                                            MaxRequestedBandwidthUlAVP(apn.max_req_bw_ul)
                                        ]),
                                        VplmnDynamicAddressAllowedAVP(VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        ])

    return ApnConfigurationAVP([
                                    ContextIdentifierAVP(apn.apn_id),
                                    ServiceSelectionAVP(apn.apn_name),
                                    PdnTypeAVP(pdn_type),
                                    EpsSubscribedQosProfileAVP([
                                                            QosClassIdentifierAVP(qci),
                                                            AllocationRetentionPriorityAVP([PriorityLevelAVP(apn.priority_level)])
                                    ]),
                                    AmbrAVP([
                                        MaxRequestedBandwidthDlAVP(apn.max_req_bw_dl),
                                        MaxRequestedBandwidthUlAVP(apn.max_req_bw_ul)
                                    ]),
                                    VplmnDynamicAddressAllowedAVP(VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED),
                                    PdnGwAllocationTypeAVP(PDN_GW_ALLOCATION_TYPE_DYNAMIC),
                                    Mip6AgentInfoAVP([
                                                MipHomeAgentHostAVP([
                                                            DestinationRealmAVP(mip6.destination_realm),
                                                            DestinationHostAVP(mip6.destination_host)
                                                ])
                                    ])
    ])


def create_list_of_apn_configuration_avp(subscriber: Subscriber) -> list:
    apn_config_avps = list()
    for apn, mip6 in zip(subscriber.apns, subscriber.mip6s):
        apn_config_avp = create_apn_configuration_avp(apn, mip6)
        apn_config_avps.append(apn_config_avp)
    return apn_config_avps


def get_subscriber_status(odb: str) -> list:
    if odb is None:
        return [SubscriberStatusAVP(SUBSCRIBER_STATUS_SERVICE_GRANTED)]

    subscriber_status_avp = SubscriberStatusAVP(SUBSCRIBER_STATUS_OPERATOR_DETERMINED_BARRING)
    operator_determined_barring_avp = OperatorDeterminedBarringAVP()

    if odb == "ODB-all-APN":
        operator_determined_barring_avp.set_bit(0)     # All Packet Oriented Services Barred

    elif odb == "ODB-HPLMN-APN":
        operator_determined_barring_avp.set_bit(1)     # Roamer Access HPLMN-AP Barred

    elif odb == "ODB-VPLMN-APN":
        operator_determined_barring_avp.set_bit(2)     # Roamer Access VPLMN-AP Barred

    return [subscriber_status_avp, operator_determined_barring_avp]


def get_schar(schar: int) -> bytes:
    if schar not in schars.keys():
        raise ValueError("Invalid Charging Characteristics value")

    return schars.get(schar)


def create_subscription_data(subscriber: Subscriber) -> list:
    apn_config_avps = create_list_of_apn_configuration_avp(subscriber)
    subscriber_status = get_subscriber_status(subscriber.odb)
    schar = get_schar(subscriber.schar)

    return [
                MsisdnAVP(subscriber.msisdn),
                StnSrAVP(subscriber.stn_sr),
                *subscriber_status,
                X3gppChargingCharacteristicsAVP(schar),
                AmbrAVP([
                            MaxRequestedBandwidthUlAVP(subscriber.max_req_bw_ul),
                            MaxRequestedBandwidthDlAVP(subscriber.max_req_bw_dl)
                ]),
                ApnConfigurationProfileAVP([
                                                ContextIdentifierAVP(subscriber.default_apn),
                                                AllApnConfigurationsIncludedIndicatorAVP(ALL_APN_CONFIGURATIONS_INCLUDED),
                                                *apn_config_avps
                ])
    ]


def create_feature_list_avp() -> FeatureListAVP:
    feature_list_avp = FeatureListAVP()
    feature_list_avp.set_bit(0)             # Operator Determined Barring of all Packet Oriented Services
    feature_list_avp.set_bit(1)             # Operator Determined Barring of Packet Oriented Services from access points that are within the HPLMN whilst the subscriber is roaming in a VPLMN
    feature_list_avp.set_bit(2)             # Operator Determined Barring of Packet Oriented Services from access points that are within the roamed to VPLMN
    return feature_list_avp


def create_supported_features() -> list:
    return [
                VendorIdAVP(VENDOR_ID_3GPP),
                FeatureListIdAVP(1),
                create_feature_list_avp()
    ]


def has_allowed_rat(request: DiameterRequest) -> bool:
    if not request.has_avp("rat_type_avp"):
        raise DiameterMissingAvp("RAT-Type AVP not found")

    if request.rat_type_avp.data != RAT_TYPE_EUTRAN:
        return False

    return True


def is_new_mme_identity(request: DiameterRequest, subscriber: Subscriber) -> bool:
    if subscriber.mme_hostname is None:
        return False

    if subscriber.mme_hostname != request.origin_host_avp.data.decode("utf-8"):
        return True

    return False


def get_context_id(request: DiameterRequest) -> int:
    if not request.has_avp("context_identifier_avp"):
        raise DiameterMissingAvp("Context-Identifier AVP not found")

    context_id = request.context_identifier_avp.data
    return convert_to_integer_from_bytes(context_id)


def get_service_selection(request: DiameterRequest) -> str:
    if not request.has_avp("service_selection_avp"):
        raise DiameterMissingAvp("Service-Selection AVP not found")

    return request.service_selection_avp.data.decode("utf-8")


def get_mip6_agent_host_destination_host(request: DiameterRequest) -> str:
    if not request.has_avp("mip6_agent_info_avp"):
        raise DiameterMissingAvp("MIP6-Agent-Info AVP not found")

    mip6_agent_info_avp = request.mip6_agent_info_avp

    if not mip6_agent_info_avp.has_avp("mip_home_agent_host_avp"):
        raise DiameterMissingAvp("MIP-Home-Agent-Host AVP not found")

    mip_home_agent_host_avp = mip6_agent_info_avp.mip_home_agent_host_avp

    if not mip_home_agent_host_avp.has_avp("destination_host_avp"):
        raise DiameterMissingAvp("Destination-Host AVP not found")

    return mip_home_agent_host_avp.destination_host_avp.data.decode("utf-8")


def get_mip6_agent_host_destination_realm(request: DiameterRequest) -> str:
    if not request.has_avp("mip6_agent_info_avp"):
        raise DiameterMissingAvp("MIP6-Agent-Info AVP not found")

    mip6_agent_info_avp = request.mip6_agent_info_avp

    if not mip6_agent_info_avp.has_avp("mip_home_agent_host_avp"):
        raise DiameterMissingAvp("MIP-Home-Agent-Host AVP not found")

    mip_home_agent_host_avp = mip6_agent_info_avp.mip_home_agent_host_avp

    if not mip_home_agent_host_avp.has_avp("destination_realm_avp"):
        raise DiameterMissingAvp("Destination-Realm AVP not found")

    return mip_home_agent_host_avp.destination_realm_avp.data.decode("utf-8")


def decode_from_plmn(plmn: bytes) -> tuple[int, int]:
    # MCC digit 1 = octet 1 (bits 1 to 4)
    # MCC digit 2 = octet 1 (bits 4 to 8)
    # MCC digit 3 = octet 2 (bits 1 to 4)

    # MNC digit 1 = octet 3 (bits 1 to 4)
    # MNC digit 2 = octet 3 (bits 4 to 8)
    # MNC digit 3 = octet 2 (bits 4 to 8)

    x0 = f"{plmn[0]:08b}"       # octet 1
    x1 = f"{plmn[1]:08b}"       # octet 2
    x2 = f"{plmn[2]:08b}"       # octet 3

    if x1[:4] == 15:
        mcc = str(int(x0[4:], 2)) + str(int(x0[:4], 2)) + str(int(x1[4:], 2))
        mnc = str(int(x2[4:], 2)) + str(int(x2[:4], 2)) + str(int(x1[:4], 2))
    else:
        mcc = str(int(x0[4:], 2)) + str(int(x0[:4], 2)) + str(int(x1[4:], 2))
        mnc = str(int(x2[4:], 2)) + str(int(x2[:4], 2))
    return int(mcc), int(mnc)


def encode_to_plmn(mcc: int, mnc: int) -> bytes:
    # octet 1 = MCC digit 2 (bits 4 to 8) + MCC digit 1 (bits 1 to 4)
    # octet 2 = MNC digit 3 (bits 4 to 8) + MCC digit 3 (bits 1 to 4)
    # octet 3 = MNC digit 2 (bits 4 to 8) + MNC digit 1 (bits 1 to 4)
    mcc_str = str(mcc)

    x0 = f"{int(mcc_str[1]):04b}" + f"{int(mcc_str[0]):04b}"        # octet 1

    if mnc < 99:
        mnc_str = str(mnc).zfill(2)

        x1 = f"{int(15):04b}" + f"{int(mcc_str[2]):04b}"            # octet 2
        x2 = f"{int(mnc_str[1]):04b}" + f"{int(mnc_str[0]):04b}"    # octet 3

    elif mnc >= 100:
        mnc_str = str(mnc).zfill(3)

        x1 = f"{int(mnc_str[2]):04b}" + f"{int(mcc_str[2]):04b}"    # octet 2
        x2 = f"{int(mnc_str[1]):04b}" + f"{int(mnc_str[0]):04b}"    # octet 3

    s = x0 + x1 + x2
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder="big")


def is_3gpp_realm_format(realm: str) -> bool:
    pattern = re.findall(r"mnc\d{3}\.mcc\d{3}\.3gppnetwork\.org", realm)
    if pattern:
        return True
    return False


def is_subscriber_roaming(request: DiameterRequest, check_remote_realm: bool = False) -> bool:
    destination_realm = request.destination_realm_avp.data.decode("utf-8")
    origin_realm = request.origin_realm_avp.data.decode("utf-8")

    if destination_realm != origin_realm:
        if check_remote_realm:
            if not is_3gpp_realm_format(origin_realm):
                raise DiameterInvalidAvpValue("Origin-Realm AVP does not "\
                                              "comply with 3GPP format: "\
                                              "mncMNC.mccMCC.3gppnetwork.org")
        return True

    return False


"PEDING UNITTESTS"
def create_missing_avp_response(proxy_response, msg: str = None, avp: DiameterAVP = None, **kwargs):
    if avp is not None:
        return proxy_response(result_code=DIAMETER_MISSING_AVP,
                              failed_avp=[avp],
                              error_message=ErrorMessageAVP(msg),
                              **kwargs)

    return proxy_response(result_code=DIAMETER_MISSING_AVP,
                          error_message=ErrorMessageAVP(msg),
                          **kwargs)


"PEDING UNITTESTS"
def create_invalid_avp_value_response(proxy_response, msg: str = None, avp: DiameterAVP = None, **kwargs):
    if avp is not None:
        return proxy_response(result_code=DIAMETER_INVALID_AVP_VALUE,
                              failed_avp=[avp],
                              error_message=ErrorMessageAVP(msg),
                              **kwargs)

    return proxy_response(result_code=DIAMETER_INVALID_AVP_VALUE,
                          error_message=ErrorMessageAVP(msg),
                          **kwargs)


"PEDING UNITTESTS"
def create_user_unknown_response(proxy_response, **kwargs):
    return proxy_response(experimental_result=create_experimental_result_data(DIAMETER_ERROR_USER_UNKNOWN),
                          **kwargs)


"PEDING UNITTESTS"
def create_authentication_data_unavailable_response(proxy_response, msg: str = None, avp: DiameterAVP = None, **kwargs):
    if avp is not None:
        return proxy_response(result_code=DIAMETER_AUTHENTICATION_DATA_UNAVAILABLE,
                              failed_avp=[avp],
                              error_message=ErrorMessageAVP(msg),
                              **kwargs)

    return proxy_response(result_code=DIAMETER_AUTHENTICATION_DATA_UNAVAILABLE,
                          error_message=ErrorMessageAVP(msg),
                          **kwargs)


"PEDING UNITTESTS"
def create_unknown_serving_node_response(proxy_response, **kwargs):
    return proxy_response(experimental_result=create_experimental_result_data(DIAMETER_ERROR_UNKOWN_SERVING_NODE),
                          **kwargs)


"PEDING UNITTESTS"
def create_rat_not_allowed_response(proxy_response, **kwargs):
    return proxy_response(experimental_result=create_experimental_result_data(DIAMETER_ERROR_RAT_NOT_ALLOWED),
           **kwargs)


"PEDING UNITTESTS"
def create_roaming_not_allowed_response(proxy_response, msg: str, **kwargs):
    return proxy_response(experimental_result=create_experimental_result_data(DIAMETER_ERROR_ROAMING_NOT_ALLOWED),
                          error_diagnostic=msg,
                          **kwargs)


"PEDING UNITTESTS"
def create_realm_not_served_response(proxy_response, msg: str, **kwargs):
    return proxy_response(result_code=DIAMETER_REALM_NOT_SERVED,
                          error_message=ErrorMessageAVP(msg),
                          **kwargs)


"PEDING UNITTESTS"
def create_unknown_eps_subscription_response(proxy_response, **kwargs):
    return proxy_response(experimental_result=create_experimental_result_data(DIAMETER_ERROR_UNKNOWN_EPS_SUBSCRIPTION),
                          **kwargs)


"PEDING UNITTESTS"
def create_success_response(proxy_response, **kwargs):
    return proxy_response(result_code=DIAMETER_SUCCESS, **kwargs)


"PEDING UNITTESTS"
class ResponseGenerator:
    def __init__(self, request: DiameterRequest, proxy_response):
        self.request = request
        self.proxy_response = proxy_response
        self.kwargs = {}


    def load_avps(self, **kwargs):
        self.kwargs = kwargs


    def missing_avp(self, msg: str = None, avp: DiameterAVP = None):
        return create_missing_avp_response(self.proxy_response, msg, avp, **self.kwargs)


    def invalid_avp_value(self, msg: str = None, avp: DiameterAVP = None):
        return create_invalid_avp_value_response(self.proxy_response, msg, avp, **self.kwargs)

    
    def user_unknown(self):
        return create_user_unknown_response(self.proxy_response, **self.kwargs)

    
    def unknown_serving_node(self):
        return create_unknown_serving_node_response(self.proxy_response, **self.kwargs)


    def rat_not_allowed(self):
        return create_rat_not_allowed_response(self.proxy_response, **self.kwargs)


    def roaming_not_allowed(self, msg: str):
        return create_roaming_not_allowed_response(self.proxy_response, msg, **self.kwargs)


    def realm_not_served(self, msg: str):
        return create_realm_not_served_response(self.proxy_response, msg, **self.kwargs)


    def unknown_eps_subscription(self):
        return create_unknown_eps_subscription_response(self.proxy_response)


    def authentication_data_unavailable(self, msg: str = None, avp: DiameterAVP = None):
        return create_authentication_data_unavailable_response(self.proxy_response, msg, avp)


    def success(self, **kwargs):
        return create_success_response(self.proxy_response, **self.kwargs, **kwargs)