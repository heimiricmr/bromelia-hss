from bromelia.avps import *
from bromelia.constants import *
from bromelia.lib.etsi_3gpp_s6a.avps import *
from bromelia.lib.etsi_3gpp_s6a import AIR # Authentication-Information-Request
from bromelia.lib.etsi_3gpp_s6a import NOR # Notify-Request
from bromelia.lib.etsi_3gpp_s6a import PUR # Purge-UE-Request
from bromelia.lib.etsi_3gpp_s6a import ULR # Update-Location-Request

class Tool:
    @classmethod
    def get_staticmethods(cls):
        staticmethods = list()
        class_attrs = cls.__dict__
        for key, value in class_attrs.items():
            forbidden_funcs = ["create", "regular_with_odb", "realm_not_served", "roaming_not_allowed"]
            if isinstance(value, staticmethod) and not key in forbidden_funcs:
                staticmethods.append((cls.__name__.lower(), key, value))
        return staticmethods

    @classmethod
    def missing_avp(cls, avp: str, **kwargs):
        request = cls.create(**kwargs)
        request.pop(avp)
        return request

    @classmethod
    def invalid_user_name_avp(cls, user_name: str = "9990000000000", **kwargs):
        return cls.create(user_name=user_name, **kwargs)

    @classmethod
    def error_user_unknown(cls, user_name: str = "000000000000000", **kwargs):
        return cls.create(user_name=user_name, **kwargs)

    @classmethod
    def regular(cls, **kwargs):
        return cls.create(user_name="999000000000001", **kwargs)

    @classmethod
    def missing_user_name_avp(cls, **kwargs):
        return cls.missing_avp("user_name_avp", **kwargs)

    @classmethod
    def missing_visited_plmn_id_avp(cls, **kwargs):
        return cls.missing_avp("visited_plmn_id_avp", **kwargs)


class Air(Tool):
    @staticmethod
    def create(**kwargs) -> AIR:
        air_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "000000000000000",
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                        VendorIdAVP(VENDOR_ID_3GPP), 
                        AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a)
                    ],
                    "requested_eutran_authentication_info": [
                        NumberOfRequestedVectorsAVP(2), 
                        ImmediateResponsePreferredAVP(1)
                    ]
        }
        return AIR(**{**air_avps, **kwargs})

    @staticmethod
    def missing_requested_eutran_authentication_info_avp(**kwargs) -> AIR:
        return Air.missing_avp(
            "requested_eutran_authentication_info_avp", 
            **kwargs
        )

    @staticmethod
    def missing_number_of_requested_vectors_avp(**kwargs) -> AIR:
        air_avps = {
                    "user_name": "999000000000001",
                    "requested_eutran_authentication_info": [
                        ImmediateResponsePreferredAVP(1)
                    ]
        }
        return Air.create(**{**air_avps, **kwargs})

    @staticmethod
    def with_immediate_response_preferred_avp(num: int = 2, **kwargs) -> AIR:
        air_avps = {
                    "user_name": "999000000000001",
                    "requested_eutran_authentication_info": [
                        NumberOfRequestedVectorsAVP(num), 
                        ImmediateResponsePreferredAVP(1)
                    ]
        }
        return Air.create(**{**air_avps, **kwargs})

    @staticmethod
    def without_immediate_response_preferred_avp(num: int = 2, **kwargs) -> AIR:
        air_avps = {
                    "user_name": "999000000000001",
                    "requested_eutran_authentication_info": [
                        NumberOfRequestedVectorsAVP(num)
                    ]
        }
        return Air.create(**{**air_avps, **kwargs})

    @staticmethod
    def too_much_immediate_response_preferred(num: int = 5, **kwargs) -> AIR:
        air_avps = {
                    "user_name": "999000000000001",
                    "requested_eutran_authentication_info": [
                        NumberOfRequestedVectorsAVP(2), 
                        ImmediateResponsePreferredAVP(num)
                    ]
        }
        return Air.create(**{**air_avps, **kwargs})

    @staticmethod
    def too_much_number_of_requested_vectors(num: int = 5, **kwargs) -> AIR:
        air_avps = {
                    "user_name": "999000000000001",
                    "requested_eutran_authentication_info": [
                        NumberOfRequestedVectorsAVP(num)
                    ]
        }
        return Air.create(**{**air_avps, **kwargs})


class Nor(Tool):
    @staticmethod
    def create(**kwargs) -> NOR:
        nor_avps = {
                "session_id": "localhost.domain",
                "origin_host": "localhost.domain",
                "origin_realm": "domain",
                "destination_realm": "domain",
                "destination_host": "remotehost.domain",
                "user_name": "000000000000000",
                "context_identifier": 3,
                "service_selection": "internet",
                "nor_flags": 0x00000000,
                "mip6_agent_info": [
                    MipHomeAgentHostAVP([
                        DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                        DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])
                ]
        }
        return NOR(**{**nor_avps, **kwargs})

    @staticmethod
    def error_unknown_serving_node(serving_node: str = "localhost2.domain", **kwargs) -> NOR:
        nor_avps = {
                "origin_host": serving_node,
                "user_name": "999000000000001",
        }
        return Nor.create(**{**nor_avps, **kwargs})

    @staticmethod
    def missing_mip6_agent_info_avp(**kwargs) -> NOR:
        return Nor.missing_avp("mip6_agent_info_avp", user_name="999000000000001", **kwargs)

    @staticmethod
    def missing_mip_home_agent_host_avp(**kwargs) -> NOR:
        nor_avps = {
                    "user_name": "999000000000001",
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        request = Nor.create(**{**nor_avps, **kwargs})
        request.mip6_agent_info_avp.pop("mip_home_agent_host_avp")
        request.refresh()
        return request

    @staticmethod
    def missing_destination_host_in_mip6_agent_info_avp(**kwargs) -> NOR:
        nor_avps = {
                    "user_name": "999000000000001",
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        request = Nor.create(**{**nor_avps, **kwargs})
        request.mip6_agent_info_avp.mip_home_agent_host_avp.pop("destination_host_avp")
        request.refresh()
        return request

    @staticmethod
    def missing_destination_realm_in_mip6_agent_info_avp(**kwargs) -> NOR:
        nor_avps = {
                    "user_name": "999000000000001",
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        request = Nor.create(**{**nor_avps, **kwargs})
        request.mip6_agent_info_avp.mip_home_agent_host_avp.pop("destination_realm_avp")
        request.refresh()
        return request


class Pur(Tool):
    @staticmethod
    def create(**kwargs) -> PUR:
        pur_avps = {
                "session_id": "localhost.domain",
                "origin_host": "localhost.domain",
                "origin_realm": "domain",
                "destination_realm": "domain",
                "destination_host": "remotehost.domain",
                "user_name": "000000000000000",
        }
        return PUR(**{**pur_avps, **kwargs})

    @staticmethod
    def error_unknown_serving_node(serving_node: str = "localhost2.domain", **kwargs) -> PUR:
        pur_avps = {
                "origin_host": serving_node,
                "user_name": "999000000000001",
        }
        return Pur.create(**{**pur_avps, **kwargs})


class Ulr(Tool):
    @staticmethod
    def create(**kwargs) -> ULR:
        ulr_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "000000000000000",
                    "rat_type": RAT_TYPE_EUTRAN,
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                        VendorIdAVP(VENDOR_ID_3GPP), 
                        AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a)
                    ],
                    "supported_features": [
                        VendorIdAVP(VENDOR_ID_3GPP), 
                        FeatureListIdAVP(1), 
                        FeatureListAVP(0xdc000200)
                    ],
                    "terminal_information": [
                        ImeiAVP("123456789000000"),
                        SoftwareVersionAVP("12")
                    ],
                    "ue_srvcc_capability": UE_SRVCC_SUPPORTED,
                    "homogeneous_support_of_ims_voice_over_ps_sessions": IMS_VOICE_OVER_PS_SUPPORTED,
        }
        return ULR(**{**ulr_avps, **kwargs})

    @staticmethod
    def rat_not_allowed(rat: bytes = RAT_TYPE_WLAN, **kwargs) -> ULR:
        return Ulr.create(rat_type=rat, **kwargs)

    @staticmethod
    def roaming_not_allowed(user_name: str, **kwargs) -> ULR:
        ulr_avps = {
                    "session_id": "localhost.mnc000.mcc999.3gppnetwork.org",
                    "origin_host": "localhost.mnc000.mcc999.3gppnetwork.org",
                    "origin_realm": "mnc000.mcc999.3gppnetwork.org",
                    "destination_realm": "mnc001.mcc999.3gppnetwork.org",
                    "destination_host": "remotehost.mnc001.mcc999.3gppnetwork.org",
                    "user_name": user_name,
        }
        return Ulr.create(**{**kwargs, **ulr_avps})

    @staticmethod
    def regular_with_odb(user_name: str, **kwargs) -> ULR:
        ulr_avps = {
                    "session_id": "localhost.mnc000.mcc999.3gppnetwork.org",
                    "origin_host": "localhost.mnc000.mcc999.3gppnetwork.org",
                    "origin_realm": "mnc000.mcc999.3gppnetwork.org",
                    "destination_realm": "mnc000.mcc999.3gppnetwork.org",
                    "destination_host": "remotehost.mnc000.mcc999.3gppnetwork.org",
                    "user_name": user_name,
        }
        return Ulr.create(**{**kwargs, **ulr_avps})

    @staticmethod
    def realm_not_served(user_name: str, **kwargs) -> ULR:
        ulr_avps = {
                    "destination_realm": "domain2",
                    "destination_host": "remotehost.domain",
                    "user_name": user_name,
        }
        return Ulr.create(**{**kwargs, **ulr_avps})
