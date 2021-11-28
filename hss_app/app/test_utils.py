# -*- coding: utf-8 -*-
"""
    hss_app.test_utils
    ~~~~~~~~~~~~~~~~~~

    This module contains the utility functions unittests.
    
    :copyright: (c) 2021 Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

import os
import unittest
from collections import namedtuple

from bromelia import Bromelia
from bromelia.lib.etsi_3gpp_s6a import AIA # AuthenticationInformationAnswer
from bromelia.lib.etsi_3gpp_s6a import AIR # AuthenticationInformationRequest
from bromelia.lib.etsi_3gpp_s6a import CLA # CancelLocationAnswer
from bromelia.lib.etsi_3gpp_s6a import CLR # CancelLocationRequest
from bromelia.lib.etsi_3gpp_s6a import NOA # NotifyAnswer
from bromelia.lib.etsi_3gpp_s6a import NOR # NotifyRequest
from bromelia.lib.etsi_3gpp_s6a import PUA # PurgeUeAnswer
from bromelia.lib.etsi_3gpp_s6a import PUR # PurgeUeRequest
from bromelia.lib.etsi_3gpp_s6a import ULA # UpdateLocationAnswer
from bromelia.lib.etsi_3gpp_s6a import ULR # UpdateLocationRequest
from bromelia.exceptions import *

from utils import *
from milenage import *


class TestGetImsi(unittest.TestCase):
    def test__from_ulr_message__valid_imsi(self):
        ulr_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "rat_type": RAT_TYPE_EUTRAN,
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                                                            VendorIdAVP(VENDOR_ID_3GPP), 
                                                            AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
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
        ulr = ULR(**ulr_avps)
    
        imsi = get_imsi(ulr)
        self.assertEqual(imsi, "999000000000000")

    def test__from_ulr_message__invalid_imsi(self):
        ulr_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "99900000000000",
                    "rat_type": RAT_TYPE_EUTRAN,
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                                                            VendorIdAVP(VENDOR_ID_3GPP), 
                                                            AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
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
        ulr = ULR(**ulr_avps)
    
        with self.assertRaises(DiameterInvalidAvpValue) as cm:
            imsi = get_imsi(ulr)
        
        self.assertEqual(cm.exception.args[0], "User-Name AVP has invalid value")

    def test__from_ulr_message__missing_avp(self):
        ulr_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "99900000000000",
                    "rat_type": RAT_TYPE_EUTRAN,
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                                                            VendorIdAVP(VENDOR_ID_3GPP), 
                                                            AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
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
        ulr = ULR(**ulr_avps)
        ulr.pop("user_name_avp")
    
        with self.assertRaises(DiameterMissingAvp) as cm:
            imsi = get_imsi(ulr)
        
        self.assertEqual(cm.exception.args[0], "User-Name AVP not found")


class TestGetVisitedPlmn(unittest.TestCase):
    def test__from_ulr_message__valid_plmn(self):
        ulr_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "rat_type": RAT_TYPE_EUTRAN,
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                                                            VendorIdAVP(VENDOR_ID_3GPP), 
                                                            AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
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
        ulr = ULR(**ulr_avps)
    
        visited_plmn = get_visited_plmn(ulr)
        self.assertEqual(visited_plmn.hex(), "09f107")

    def test__from_ulr_message__missing_avp(self):
        ulr_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "rat_type": RAT_TYPE_EUTRAN,
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                                                            VendorIdAVP(VENDOR_ID_3GPP), 
                                                            AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
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
        ulr = ULR(**ulr_avps)
        ulr.pop("visited_plmn_id_avp")

        with self.assertRaises(DiameterMissingAvp) as cm:
            visited_plmn = get_visited_plmn(ulr)
        
        self.assertEqual(cm.exception.args[0], "Visited-PLMN-Id AVP not found")


class TestGetNumberOfRequestedVectors(unittest.TestCase):
    def test__from_air_message__valid_number_of_requested_vectors(self):
        air_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [VendorIdAVP(VENDOR_ID_3GPP), AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)],
                    "requested_eutran_authentication_info": [NumberOfRequestedVectorsAVP(2), ImmediateResponsePreferredAVP(1)]
        }
        air = AIR(**air_avps)
    
        num_of_requested_vectors = get_num_of_requested_vectors(air)
        self.assertEqual(num_of_requested_vectors, 2)

    def test__from_air_message__missing_avp__1(self):
        air_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [VendorIdAVP(VENDOR_ID_3GPP), AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)],
                    "requested_eutran_authentication_info": [ImmediateResponsePreferredAVP(1)]
        }
        air = AIR(**air_avps)
 
        with self.assertRaises(DiameterMissingAvp) as cm:
            num_of_requested_vectors = get_num_of_requested_vectors(air)

        self.assertEqual(cm.exception.args[0], "Number-Of-Requested-Vectors AVP not found")

    def test__from_air_message__missing_avp__2(self):
        air_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [VendorIdAVP(VENDOR_ID_3GPP), AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)],
        }
        air = AIR(**air_avps)
 
        with self.assertRaises(DiameterMissingAvp) as cm:
            num_of_requested_vectors = get_num_of_requested_vectors(air)

        self.assertEqual(cm.exception.args[0], "Requested-EUTRAN-Authentication-Info AVP not found")


class TestGetImmediateResponsePreferred(unittest.TestCase):
    def test__from_air_message__valid_number_of_requested_vectors(self):
        air_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [VendorIdAVP(VENDOR_ID_3GPP), AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)],
                    "requested_eutran_authentication_info": [NumberOfRequestedVectorsAVP(2), ImmediateResponsePreferredAVP(1)]
        }
        air = AIR(**air_avps)
    
        immediate_response_preferred = get_immediate_response_preferred(air)
        self.assertEqual(immediate_response_preferred, 1)

    def test__from_air_message__missing_avp__1(self):
        air_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [VendorIdAVP(VENDOR_ID_3GPP), AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)],
                    "requested_eutran_authentication_info": [NumberOfRequestedVectorsAVP(2)]
        }
        air = AIR(**air_avps)
 
        immediate_response_preferred = get_immediate_response_preferred(air)
        self.assertIsNone(immediate_response_preferred)

    def test__from_air_message__missing_avp__2(self):
        air_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [VendorIdAVP(VENDOR_ID_3GPP), AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)],
        }
        air = AIR(**air_avps)
 
        with self.assertRaises(DiameterMissingAvp) as cm:
            immediate_response_preferred = get_immediate_response_preferred(air)

        self.assertEqual(cm.exception.args[0], "Requested-EUTRAN-Authentication-Info AVP not found")


class TestGenerateVectors(unittest.TestCase):
    def test__generate_vectors__1(self):
        num_of_vectors = 1
        key = bytes.fromhex("465b5ce8b199b49faa5f0a2ee238a6bc")
        opc = bytes.fromhex("cd63cb71954a9f4e48a5994e37a02baf")
        amf = bytes.fromhex("b9b9")
        sqn = bytes.fromhex("ff9bb4d0b607")
        plmn = bytes.fromhex("09f107")

        vectors, sqn = generate_vectors(num_of_vectors, key, opc, amf, sqn, plmn)
        rand, xres, autn, kasme = vectors[0]

        self.assertEqual(len(vectors), 1)

        _rand, _xres, _autn, _kasme = calculate_eutran_vector(key, opc, amf, sqn, plmn, rand)

        self.assertEqual(rand, _rand)
        self.assertEqual(xres, _xres)
        self.assertEqual(autn, _autn)
        self.assertEqual(kasme, _kasme)

    def test__generate_vectors__2(self):
        num_of_vectors = 2
        key = bytes.fromhex("465b5ce8b199b49faa5f0a2ee238a6bc")
        opc = bytes.fromhex("cd63cb71954a9f4e48a5994e37a02baf")
        amf = bytes.fromhex("b9b9")
        sqn = bytes.fromhex("ff9bb4d0b607")
        plmn = bytes.fromhex("09f107")

        vectors, sqn = generate_vectors(num_of_vectors, key, opc, amf, sqn, plmn)

        self.assertEqual(len(vectors), 2)

        for vector in vectors:
            rand, xres, autn, kasme = vector

            _rand, _xres, _autn, _kasme = calculate_eutran_vector(key, opc, amf, sqn, plmn, rand)

            self.assertEqual(rand, _rand)
            self.assertEqual(xres, _xres)
            self.assertEqual(autn, _autn)
            self.assertEqual(kasme, _kasme)


class TestGenerateAuthenticationInfoAvpData(unittest.TestCase):
    def test__generate_authentication_info_avp_data__1(self):
        rand = bytes.fromhex("23553cbe9637a89d218ae64dae47bf35")
        xres = bytes.fromhex("a54211d5e3ba50bf")
        autn = bytes.fromhex("55f328b43577b9b94a9ffac354dfafb3")
        kasme = bytes.fromhex("00c73bac435945a7c5cf3565c0d3c64375416b255f0bd65d74f40e60c90a280a")

        vector = Vector(rand, xres, autn, kasme)
        vectors = [vector]

        eutran_vector_avps = generate_authentication_info_avp_data(vectors)
        eutran_vector_avp = eutran_vector_avps[0]

        self.assertEqual(len(eutran_vector_avps), 1)
        self.assertEqual(eutran_vector_avp.code, E_UTRAN_VECTOR_AVP_CODE)

        with self.assertRaises(AttributeError) as cm:
            eutran_vector_avp.item_number_avp.code
        
        self.assertEqual(cm.exception.args[0], "'EUtranVectorAVP' object has no attribute 'item_number_avp'")

        self.assertEqual(eutran_vector_avp.rand_avp.code, RAND_AVP_CODE)
        self.assertEqual(eutran_vector_avp.rand_avp.data, rand)

        self.assertEqual(eutran_vector_avp.xres_avp.code, XRES_AVP_CODE)
        self.assertEqual(eutran_vector_avp.xres_avp.data, xres)

        self.assertEqual(eutran_vector_avp.autn_avp.code, AUTN_AVP_CODE)
        self.assertEqual(eutran_vector_avp.autn_avp.data, autn)

        self.assertEqual(eutran_vector_avp.kasme_avp.code, KASME_AVP_CODE)
        self.assertEqual(eutran_vector_avp.kasme_avp.data, kasme)

    def test__generate_authentication_info_avp_data__2(self):
        rand = bytes.fromhex("23553cbe9637a89d218ae64dae47bf35")
        xres = bytes.fromhex("a54211d5e3ba50bf")
        autn = bytes.fromhex("55f328b43577b9b94a9ffac354dfafb3")
        kasme = bytes.fromhex("00c73bac435945a7c5cf3565c0d3c64375416b255f0bd65d74f40e60c90a280a")

        vector = Vector(rand, xres, autn, kasme)

        vectors = list()
        for _ in range(2):
            vectors.append(vector)

        eutran_vector_avps = generate_authentication_info_avp_data(vectors)
        self.assertEqual(len(eutran_vector_avps), 2)

        for index, eutran_vector_avp in enumerate(eutran_vector_avps, 1):
            self.assertEqual(eutran_vector_avp.code, E_UTRAN_VECTOR_AVP_CODE)

            self.assertEqual(eutran_vector_avp.item_number_avp.code, ITEM_NUMBER_AVP_CODE)
            self.assertEqual(eutran_vector_avp.item_number_avp.data, convert_to_4_bytes(index))

            self.assertEqual(eutran_vector_avp.rand_avp.code, RAND_AVP_CODE)
            self.assertEqual(eutran_vector_avp.rand_avp.data, rand)

            self.assertEqual(eutran_vector_avp.xres_avp.code, XRES_AVP_CODE)
            self.assertEqual(eutran_vector_avp.xres_avp.data, xres)

            self.assertEqual(eutran_vector_avp.autn_avp.code, AUTN_AVP_CODE)
            self.assertEqual(eutran_vector_avp.autn_avp.data, autn)

            self.assertEqual(eutran_vector_avp.kasme_avp.code, KASME_AVP_CODE)
            self.assertEqual(eutran_vector_avp.kasme_avp.data, kasme)

    def test__generate_authentication_info_avp_data__3(self):
        rand = bytes.fromhex("23553cbe9637a89d218ae64dae47bf35")
        xres = bytes.fromhex("a54211d5e3ba50bf")
        autn = bytes.fromhex("55f328b43577b9b94a9ffac354dfafb3")
        kasme = bytes.fromhex("00c73bac435945a7c5cf3565c0d3c64375416b255f0bd65d74f40e60c90a280a")

        vector = Vector(rand, xres, autn, kasme)

        vectors = list()
        for _ in range(5):
            vectors.append(vector)

        eutran_vector_avps = generate_authentication_info_avp_data(vectors)
        self.assertEqual(len(eutran_vector_avps), 5)

        for index, eutran_vector_avp in enumerate(eutran_vector_avps, 1):
            self.assertEqual(eutran_vector_avp.code, E_UTRAN_VECTOR_AVP_CODE)

            self.assertEqual(eutran_vector_avp.item_number_avp.code, ITEM_NUMBER_AVP_CODE)
            self.assertEqual(eutran_vector_avp.item_number_avp.data, convert_to_4_bytes(index))

            self.assertEqual(eutran_vector_avp.rand_avp.code, RAND_AVP_CODE)
            self.assertEqual(eutran_vector_avp.rand_avp.data, rand)

            self.assertEqual(eutran_vector_avp.xres_avp.code, XRES_AVP_CODE)
            self.assertEqual(eutran_vector_avp.xres_avp.data, xres)

            self.assertEqual(eutran_vector_avp.autn_avp.code, AUTN_AVP_CODE)
            self.assertEqual(eutran_vector_avp.autn_avp.data, autn)

            self.assertEqual(eutran_vector_avp.kasme_avp.code, KASME_AVP_CODE)
            self.assertEqual(eutran_vector_avp.kasme_avp.data, kasme)


class TestIsResyncRequired(unittest.TestCase):
    def test__from_air_message__valid_resynchronization_info__1(self):
        air_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [VendorIdAVP(VENDOR_ID_3GPP), AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)],
                    "requested_eutran_authentication_info": [
                                                                NumberOfRequestedVectorsAVP(2), 
                                                                ImmediateResponsePreferredAVP(1),
                                                                ReSynchronizationInfoAVP(bytes.fromhex("1764d7bc135c8f72cbb039bd58b66bbd46af726351ae673f149a4f618c54"))
                    ]
        }
        air = AIR(**air_avps)
        self.assertTrue(is_resync_required(air))

    def test__from_air_message__valid_resynchronization_info__2(self):
        air_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [VendorIdAVP(VENDOR_ID_3GPP), AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)],
                    "requested_eutran_authentication_info": [
                                                                NumberOfRequestedVectorsAVP(2), 
                                                                ImmediateResponsePreferredAVP(1)
                    ]
        }
        air = AIR(**air_avps)
        self.assertFalse(is_resync_required(air))

    def test__from_air_message__missing_avp__1(self):
        air_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [VendorIdAVP(VENDOR_ID_3GPP), AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)],
        }
        air = AIR(**air_avps)

        with self.assertRaises(DiameterMissingAvp) as cm:
            self.assertTrue(is_resync_required(air))

        self.assertEqual(cm.exception.args[0], "Requested-EUTRAN-Authentication-Info AVP not found")


class TestReSyncData(unittest.TestCase):
    def test__from_air_message__valid_resync_data(self):
        air_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [VendorIdAVP(VENDOR_ID_3GPP), AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)],
                    "requested_eutran_authentication_info": [
                                                                NumberOfRequestedVectorsAVP(2), 
                                                                ImmediateResponsePreferredAVP(1),
                                                                ReSynchronizationInfoAVP(bytes.fromhex("1764d7bc135c8f72cbb039bd58b66bbd46af726351ae673f149a4f618c54"))
                    ]
        }
        air = AIR(**air_avps)
        rand, auts = get_resync_data(air)

        self.assertEqual(rand.hex(), "1764d7bc135c8f72cbb039bd58b66bbd")
        self.assertEqual(auts.hex(), "46af726351ae673f149a4f618c54")

    def test__from_air_message__missing_avp__1(self):
        air_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [VendorIdAVP(VENDOR_ID_3GPP), AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)],
        }
        air = AIR(**air_avps)

        with self.assertRaises(DiameterMissingAvp) as cm:
            self.assertTrue(is_resync_required(air))

        self.assertEqual(cm.exception.args[0], "Requested-EUTRAN-Authentication-Info AVP not found")


class TestUeSrvccSupport(unittest.TestCase):
    def test__from_ulr_message__valid_ue_srvcc_support__1(self):
        ulr_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "rat_type": RAT_TYPE_EUTRAN,
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                                                            VendorIdAVP(VENDOR_ID_3GPP), 
                                                            AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
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
        ulr = ULR(**ulr_avps)
    
        ue_srvcc_support = is_ue_srvcc_supported(ulr)
        self.assertTrue(ue_srvcc_support, IMS_VOICE_OVER_PS_SUPPORTED)

    def test__from_ulr_message__valid_ue_srvcc_support__2(self):
        ulr_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "rat_type": RAT_TYPE_EUTRAN,
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                                                            VendorIdAVP(VENDOR_ID_3GPP), 
                                                            AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
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
                    "ue_srvcc_capability": UE_SRVCC_NOT_SUPPORTED,
                    "homogeneous_support_of_ims_voice_over_ps_sessions": IMS_VOICE_OVER_PS_SUPPORTED,
        }
        ulr = ULR(**ulr_avps)
    
        ue_srvcc_support = is_ue_srvcc_supported(ulr)
        self.assertFalse(ue_srvcc_support, UE_SRVCC_NOT_SUPPORTED)

    def test__from_ulr_message__missing_avp(self):
        ulr_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "rat_type": RAT_TYPE_EUTRAN,
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                                                            VendorIdAVP(VENDOR_ID_3GPP), 
                                                            AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
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
                    "homogeneous_support_of_ims_voice_over_ps_sessions": IMS_VOICE_OVER_PS_SUPPORTED,
        }
        ulr = ULR(**ulr_avps)
    
        ue_srvcc_support = is_ue_srvcc_supported(ulr)
        self.assertIsNone(ue_srvcc_support)


class TestCreateExperimentalResultData(unittest.TestCase):
    def test__diameter_user_data_not_available(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_USER_DATA_NOT_AVAILABLE)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_USER_DATA_NOT_AVAILABLE)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_prior_update_in_progress(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_PRIOR_UPDATE_IN_PROGRESS)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_PRIOR_UPDATE_IN_PROGRESS)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_authentication_data_unavailable(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_AUTHENTICATION_DATA_UNAVAILABLE)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_AUTHENTICATION_DATA_UNAVAILABLE)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_user_unknown(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_USER_UNKNOWN)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_USER_UNKNOWN)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_identities_dont_match(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_IDENTITIES_DONT_MATCH)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_IDENTITIES_DONT_MATCH)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_identities_not_registered(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_IDENTITY_NOT_REGISTERED)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_IDENTITY_NOT_REGISTERED)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_roaming_not_allowed(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_ROAMING_NOT_ALLOWED)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_ROAMING_NOT_ALLOWED)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_identity_already_registered(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_IDENTITY_ALREADY_REGISTERED)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_IDENTITY_ALREADY_REGISTERED)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_auth_scheme_not_supported(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_AUTH_SCHEME_NOT_SUPPORTED)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_AUTH_SCHEME_NOT_SUPPORTED)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_in_assignment_type(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_IN_ASSIGNMENT_TYPE)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_IN_ASSIGNMENT_TYPE)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_too_much_data(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_TOO_MUCH_DATA)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_TOO_MUCH_DATA)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_not_supported_user_data(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_NOT_SUPPORTED_USER_DATA)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_NOT_SUPPORTED_USER_DATA)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_feature_unsupported(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_FEATURE_UNSUPPORTED)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_FEATURE_UNSUPPORTED)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_serving_node_feature_unsupported(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_SERVING_NODE_FEATURE_UNSUPPORTED)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_SERVING_NODE_FEATURE_UNSUPPORTED)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_user_data_not_recognized(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_USER_DATA_NOT_RECOGNIZED)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_USER_DATA_NOT_RECOGNIZED)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_operation_not_allowed(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_OPERATION_NOT_ALLOWED)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_OPERATION_NOT_ALLOWED)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_user_data_cannot_be_read(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_USER_DATA_CANNOT_BE_READ)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_USER_DATA_CANNOT_BE_READ)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_user_data_cannot_be_modified(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_USER_DATA_CANNOT_BE_MODIFIED)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_USER_DATA_CANNOT_BE_MODIFIED)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_user_data_cannot_be_notified(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_USER_DATA_CANNOT_BE_NOTIFIED)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_USER_DATA_CANNOT_BE_NOTIFIED)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_transparent_data_out_of_sync(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_TRANSPARENT_DATA_OUT_OF_SYNC)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_TRANSPARENT_DATA_OUT_OF_SYNC)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_subs_data_absent(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_SUBS_DATA_ABSENT)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_SUBS_DATA_ABSENT)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_no_subscription_to_data(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_NO_SUBSCRIPTION_TO_DATA)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_NO_SUBSCRIPTION_TO_DATA)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_dsai_not_available(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_DSAI_NOT_AVAILABLE)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_DSAI_NOT_AVAILABLE)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_unknown_eps_subscription(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_UNKNOWN_EPS_SUBSCRIPTION)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_UNKNOWN_EPS_SUBSCRIPTION)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_rat_not_allowed(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_RAT_NOT_ALLOWED)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_RAT_NOT_ALLOWED)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_equipment_unknown(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_EQUIPMENT_UNKNOWN)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_EQUIPMENT_UNKNOWN)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_unknown_serving_node(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_UNKOWN_SERVING_NODE)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_UNKOWN_SERVING_NODE)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_user_no_non_3gpp_subscription(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_USER_NO_NON_3GPP_SUBSCRIPTION)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_USER_NO_NON_3GPP_SUBSCRIPTION)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_user_no_apn_subscription(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_USER_NO_APN_SUBSCRIPTION)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_USER_NO_APN_SUBSCRIPTION)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

    def test__diameter_error_rat_type_not_allowed(self):
        experimental_result_code_avp, vendor_id_avp = create_experimental_result_data(DIAMETER_ERROR_RAT_TYPE_NOT_ALLOWED)

        self.assertEqual(experimental_result_code_avp.get_code(), 298)
        self.assertEqual(experimental_result_code_avp.get_length(), 12)
        self.assertEqual(experimental_result_code_avp.data, DIAMETER_ERROR_RAT_TYPE_NOT_ALLOWED)

        self.assertEqual(vendor_id_avp.get_code(), 266)
        self.assertEqual(vendor_id_avp.get_length(), 12)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)


class TestGenerateEutranVectorAvp(unittest.TestCase):
    def test__generate_eutran_vector_avp__1__use_index_true(self):
        rand = bytes.fromhex("23553cbe9637a89d218ae64dae47bf35")
        xres = bytes.fromhex("a54211d5e3ba50bf")
        autn = bytes.fromhex("55f328b43577b9b94a9ffac354dfafb3")
        kasme = bytes.fromhex("00c73bac435945a7c5cf3565c0d3c64375416b255f0bd65d74f40e60c90a280a")

        vector = Vector(rand, xres, autn, kasme)
        eutran_vector_avp = generate_eutran_vector_avp(1, vector)

        self.assertEqual(eutran_vector_avp.code, E_UTRAN_VECTOR_AVP_CODE)

        self.assertEqual(eutran_vector_avp.item_number_avp.code, ITEM_NUMBER_AVP_CODE)
        self.assertEqual(eutran_vector_avp.item_number_avp.data, bytes.fromhex("00000001"))

        self.assertEqual(eutran_vector_avp.rand_avp.code, RAND_AVP_CODE)
        self.assertEqual(eutran_vector_avp.rand_avp.data, rand)

        self.assertEqual(eutran_vector_avp.xres_avp.code, XRES_AVP_CODE)
        self.assertEqual(eutran_vector_avp.xres_avp.data, xres)

        self.assertEqual(eutran_vector_avp.autn_avp.code, AUTN_AVP_CODE)
        self.assertEqual(eutran_vector_avp.autn_avp.data, autn)

        self.assertEqual(eutran_vector_avp.kasme_avp.code, KASME_AVP_CODE)
        self.assertEqual(eutran_vector_avp.kasme_avp.data, kasme)

    def test__generate_eutran_vector_avp__2__use_index_true(self):
        rand = bytes.fromhex("23553cbe9637a89d218ae64dae47bf35")
        xres = bytes.fromhex("a54211d5e3ba50bf")
        autn = bytes.fromhex("55f328b43577b9b94a9ffac354dfafb3")
        kasme = bytes.fromhex("00c73bac435945a7c5cf3565c0d3c64375416b255f0bd65d74f40e60c90a280a")

        vector = Vector(rand, xres, autn, kasme)
        eutran_vector_avp = generate_eutran_vector_avp(5, vector)

        self.assertEqual(eutran_vector_avp.code, E_UTRAN_VECTOR_AVP_CODE)

        self.assertEqual(eutran_vector_avp.item_number_avp.code, ITEM_NUMBER_AVP_CODE)
        self.assertEqual(eutran_vector_avp.item_number_avp.data, bytes.fromhex("00000005"))

        self.assertEqual(eutran_vector_avp.rand_avp.code, RAND_AVP_CODE)
        self.assertEqual(eutran_vector_avp.rand_avp.data, rand)

        self.assertEqual(eutran_vector_avp.xres_avp.code, XRES_AVP_CODE)
        self.assertEqual(eutran_vector_avp.xres_avp.data, xres)

        self.assertEqual(eutran_vector_avp.autn_avp.code, AUTN_AVP_CODE)
        self.assertEqual(eutran_vector_avp.autn_avp.data, autn)

        self.assertEqual(eutran_vector_avp.kasme_avp.code, KASME_AVP_CODE)
        self.assertEqual(eutran_vector_avp.kasme_avp.data, kasme)

    def test__generate_eutran_vector_avp__3__use_index_false(self):
        rand = bytes.fromhex("23553cbe9637a89d218ae64dae47bf35")
        xres = bytes.fromhex("a54211d5e3ba50bf")
        autn = bytes.fromhex("55f328b43577b9b94a9ffac354dfafb3")
        kasme = bytes.fromhex("00c73bac435945a7c5cf3565c0d3c64375416b255f0bd65d74f40e60c90a280a")

        vector = Vector(rand, xres, autn, kasme)
        eutran_vector_avp = generate_eutran_vector_avp(5, vector, use_index=False)

        self.assertEqual(eutran_vector_avp.code, E_UTRAN_VECTOR_AVP_CODE)

        with self.assertRaises(AttributeError) as cm:
            eutran_vector_avp.item_number_avp.code
        
        self.assertEqual(cm.exception.args[0], "'EUtranVectorAVP' object has no attribute 'item_number_avp'")

        self.assertEqual(eutran_vector_avp.rand_avp.code, RAND_AVP_CODE)
        self.assertEqual(eutran_vector_avp.rand_avp.data, rand)

        self.assertEqual(eutran_vector_avp.xres_avp.code, XRES_AVP_CODE)
        self.assertEqual(eutran_vector_avp.xres_avp.data, xres)

        self.assertEqual(eutran_vector_avp.autn_avp.code, AUTN_AVP_CODE)
        self.assertEqual(eutran_vector_avp.autn_avp.data, autn)

        self.assertEqual(eutran_vector_avp.kasme_avp.code, KASME_AVP_CODE)
        self.assertEqual(eutran_vector_avp.kasme_avp.data, kasme)


class TestGetPdnType(unittest.TestCase):
    def test__get_pdn_type__invalid(self):
        with self.assertRaises(ValueError) as cm:
            pdn_type = get_pdn_type("IPv5")
        
        self.assertEqual(cm.exception.args[0], "Invalid PDN-Type value")

    def test__get_pdn_type__ipv4(self):
        self.assertEqual(get_pdn_type("IPv4"), PDN_TYPE_IPV4)

    def test__get_pdn_type__ipv6(self):
        self.assertEqual(get_pdn_type("IPv6"), PDN_TYPE_IPV6)

    def test__get_pdn_type__ipv4v6(self):
        self.assertEqual(get_pdn_type("IPv4v6"), PDN_TYPE_IPV4V6)

    def test__get_pdn_type__ipv4orv6(self):
        self.assertEqual(get_pdn_type("IPv4orv6"), PDN_TYPE_IPV4_OR_IPV6)


class TestGetQci(unittest.TestCase):
    def test__get_qci__invalid(self):
        with self.assertRaises(ValueError) as cm:
            qci = get_qci(824)
        
        self.assertEqual(cm.exception.args[0], "Invalid QCI value")

    def test__get_qci__1(self):
        self.assertEqual(get_qci(1), QCI_1)

    def test__get_qci__2(self):
        self.assertEqual(get_qci(2), QCI_2)

    def test__get_qci__3(self):
        self.assertEqual(get_qci(3), QCI_3)

    def test__get_qci__4(self):
        self.assertEqual(get_qci(4), QCI_4)

    def test__get_qci__5(self):
        self.assertEqual(get_qci(5), QCI_5)

    def test__get_qci__6(self):
        self.assertEqual(get_qci(6), QCI_6)

    def test__get_qci__7(self):
        self.assertEqual(get_qci(7), QCI_7)

    def test__get_qci__8(self):
        self.assertEqual(get_qci(8), QCI_8)

    def test__get_qci__9(self):
        self.assertEqual(get_qci(9), QCI_9)

    def test__get_qci__65(self):
        self.assertEqual(get_qci(65), QCI_65)

    def test__get_qci__66(self):
        self.assertEqual(get_qci(66), QCI_66)

    def test__get_qci__69(self):
        self.assertEqual(get_qci(69), QCI_69)

    def test__get_qci__70(self):
        self.assertEqual(get_qci(70), QCI_70)


class TestCreateApnConfigurationAvp(unittest.TestCase):
    def setUp(self):
        self.Mip6 = namedtuple("Mip6s", ["context_id", "service_selection", "destination_realm", "destination_host"])
        self.Apn = namedtuple("Apns", ["apn_id", "apn_name", "pdn_type", "qci", "priority_level", "max_req_bw_dl", "max_req_bw_ul"])

    def test__create_apn_configuration_avp__1(self):
        apn = self.Apn(apn_id=1, apn_name="internet", pdn_type="IPv4", qci=9, priority_level=8, max_req_bw_dl=999999999, max_req_bw_ul=999999999)
        mip6 = self.Mip6(context_id=1, service_selection="internet", destination_realm="epc.mncXXX.mccYYY.3gppnetwork.org", destination_host="topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")

        apn_configuration_avp = create_apn_configuration_avp(apn, mip6)

        self.assertEqual(apn_configuration_avp.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(apn_configuration_avp.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(apn_configuration_avp.context_identifier_avp.data, convert_to_4_bytes(1))
        self.assertEqual(apn_configuration_avp.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(apn_configuration_avp.service_selection_avp.data, b"internet")
        self.assertEqual(apn_configuration_avp.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(apn_configuration_avp.pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(apn_configuration_avp.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(apn_configuration_avp.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(apn_configuration_avp.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        self.assertEqual(apn_configuration_avp.pdn_gw_allocation_type_avp.code, PDN_GW_ALLOCATION_TYPE_AVP_CODE)
        self.assertEqual(apn_configuration_avp.pdn_gw_allocation_type_avp.data, PDN_GW_ALLOCATION_TYPE_DYNAMIC)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.code, MIP6_AGENT_INFO_AVP_CODE)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.code, MIP_HOME_AGENT_HOST_AVP_CODE)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.code, DESTINATION_REALM_AVP_CODE)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.data, b"epc.mncXXX.mccYYY.3gppnetwork.org")
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.code, DESTINATION_HOST_AVP_CODE)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.data, b"topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")

    def test__create_apn_configuration_avp__2(self):
        apn = self.Apn(apn_id=4, apn_name="mms", pdn_type="IPv4", qci=9, priority_level=8, max_req_bw_dl=256, max_req_bw_ul=256)
        mip6 = self.Mip6(context_id=4, service_selection="mms", destination_realm="epc.mncXXX.mccYYY.3gppnetwork.org", destination_host="topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
        
        apn_configuration_avp = create_apn_configuration_avp(apn, mip6)

        self.assertEqual(apn_configuration_avp.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(apn_configuration_avp.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(apn_configuration_avp.context_identifier_avp.data, convert_to_4_bytes(4))
        self.assertEqual(apn_configuration_avp.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(apn_configuration_avp.service_selection_avp.data, b"mms")
        self.assertEqual(apn_configuration_avp.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(apn_configuration_avp.pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(apn_configuration_avp.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(apn_configuration_avp.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(apn_configuration_avp.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        self.assertEqual(apn_configuration_avp.pdn_gw_allocation_type_avp.code, PDN_GW_ALLOCATION_TYPE_AVP_CODE)
        self.assertEqual(apn_configuration_avp.pdn_gw_allocation_type_avp.data, PDN_GW_ALLOCATION_TYPE_DYNAMIC)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.code, MIP6_AGENT_INFO_AVP_CODE)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.code, MIP_HOME_AGENT_HOST_AVP_CODE)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.code, DESTINATION_REALM_AVP_CODE)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.data, b"epc.mncXXX.mccYYY.3gppnetwork.org")
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.code, DESTINATION_HOST_AVP_CODE)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.data, b"topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")

    def test__create_apn_configuration_avp__3(self):
        apn = self.Apn(apn_id=3, apn_name="xcap", pdn_type="IPv6", qci=9, priority_level=8, max_req_bw_dl=256, max_req_bw_ul=256)
        mip6 = self.Mip6(context_id=3, service_selection="xcap", destination_realm="epc.mncXXX.mccYYY.3gppnetwork.org", destination_host="topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
        
        apn_configuration_avp = create_apn_configuration_avp(apn, mip6)

        self.assertEqual(apn_configuration_avp.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(apn_configuration_avp.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(apn_configuration_avp.context_identifier_avp.data, convert_to_4_bytes(3))
        self.assertEqual(apn_configuration_avp.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(apn_configuration_avp.service_selection_avp.data, b"xcap")
        self.assertEqual(apn_configuration_avp.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(apn_configuration_avp.pdn_type_avp.data, PDN_TYPE_IPV6)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(apn_configuration_avp.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(apn_configuration_avp.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(apn_configuration_avp.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        self.assertEqual(apn_configuration_avp.pdn_gw_allocation_type_avp.code, PDN_GW_ALLOCATION_TYPE_AVP_CODE)
        self.assertEqual(apn_configuration_avp.pdn_gw_allocation_type_avp.data, PDN_GW_ALLOCATION_TYPE_DYNAMIC)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.code, MIP6_AGENT_INFO_AVP_CODE)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.code, MIP_HOME_AGENT_HOST_AVP_CODE)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.code, DESTINATION_REALM_AVP_CODE)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.data, b"epc.mncXXX.mccYYY.3gppnetwork.org")
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.code, DESTINATION_HOST_AVP_CODE)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.data, b"topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")

    def test__create_apn_configuration_avp__4(self):
        apn = self.Apn(apn_id=824, apn_name="ims", pdn_type="IPv4v6", qci=5, priority_level=8, max_req_bw_dl=256, max_req_bw_ul=256)
        mip6 = self.Mip6(context_id=824, service_selection="ims", destination_realm="epc.mncXXX.mccYYY.3gppnetwork.org", destination_host="topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
        
        apn_configuration_avp = create_apn_configuration_avp(apn, mip6)

        self.assertEqual(apn_configuration_avp.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(apn_configuration_avp.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(apn_configuration_avp.context_identifier_avp.data, convert_to_4_bytes(824))
        self.assertEqual(apn_configuration_avp.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(apn_configuration_avp.service_selection_avp.data, b"ims")
        self.assertEqual(apn_configuration_avp.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(apn_configuration_avp.pdn_type_avp.data, PDN_TYPE_IPV4V6)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(5))
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(apn_configuration_avp.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(apn_configuration_avp.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(apn_configuration_avp.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        self.assertEqual(apn_configuration_avp.pdn_gw_allocation_type_avp.code, PDN_GW_ALLOCATION_TYPE_AVP_CODE)
        self.assertEqual(apn_configuration_avp.pdn_gw_allocation_type_avp.data, PDN_GW_ALLOCATION_TYPE_DYNAMIC)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.code, MIP6_AGENT_INFO_AVP_CODE)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.code, MIP_HOME_AGENT_HOST_AVP_CODE)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.code, DESTINATION_REALM_AVP_CODE)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.data, b"epc.mncXXX.mccYYY.3gppnetwork.org")
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.code, DESTINATION_HOST_AVP_CODE)
        self.assertEqual(apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.data, b"topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")


class TestCreateListOfApnConfigurationAvp(unittest.TestCase):
    def setUp(self):
        self.Mip6 = namedtuple("Mip6s", ["context_id", "service_selection", "destination_realm", "destination_host"])
        self.Subscriber = namedtuple("Subscriber", ["msisdn", "stn_sr", "odb", "schar", "max_req_bw_ul", "max_req_bw_dl", "default_apn", "apns", "mip6s"])
        self.Apn = namedtuple("Apns", ["apn_id", "apn_name", "pdn_type", "qci", "priority_level", "max_req_bw_dl", "max_req_bw_ul"])

    def test__create_list_of_apn_configuration_avp__1(self):
        subs = {
            "msisdn": 5521000000001,
            "stn_sr": 5500599999999,
            "odb": None,
            "schar": 8,
            "max_req_bw_ul": 256,
            "max_req_bw_dl": 256,
            "default_apn": 824,
            "apns": [
                self.Apn(apn_id=1, apn_name="internet", pdn_type="IPv4", qci=9, priority_level=8, max_req_bw_dl=999999999, max_req_bw_ul=999999999),
                self.Apn(apn_id=4, apn_name="mms", pdn_type="IPv4", qci=9, priority_level=8, max_req_bw_dl=256, max_req_bw_ul=256),
                self.Apn(apn_id=3, apn_name="xcap", pdn_type="IPv6", qci=9, priority_level=8, max_req_bw_dl=256, max_req_bw_ul=256),
                self.Apn(apn_id=824, apn_name="ims", pdn_type="IPv4v6", qci=5, priority_level=8, max_req_bw_dl=256, max_req_bw_ul=256),
            ],
            "mip6s": [
                self.Mip6(context_id=1, service_selection="internet", destination_realm="epc.mncXXX.mccYYY.3gppnetwork.org", destination_host="topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org"),
                self.Mip6(context_id=4, service_selection="mms", destination_realm="epc.mncXXX.mccYYY.3gppnetwork.org", destination_host="topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org"),
                self.Mip6(context_id=3, service_selection="xcap", destination_realm="epc.mncXXX.mccYYY.3gppnetwork.org", destination_host="topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org"),
                self.Mip6(context_id=824, service_selection="ims", destination_realm="epc.mncXXX.mccYYY.3gppnetwork.org", destination_host="topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org"),
            ]
        }
        subscriber = self.Subscriber(**subs)

        apn_config_avps = create_list_of_apn_configuration_avp(subscriber)

        self.assertEqual(apn_config_avps[0].code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(apn_config_avps[0].context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(apn_config_avps[0].context_identifier_avp.data, convert_to_4_bytes(1))
        self.assertEqual(apn_config_avps[0].service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(apn_config_avps[0].service_selection_avp.data, b"internet")
        self.assertEqual(apn_config_avps[0].pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(apn_config_avps[0].pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(apn_config_avps[0].eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(apn_config_avps[0].eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(apn_config_avps[0].eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(apn_config_avps[0].eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(apn_config_avps[0].eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(apn_config_avps[0].eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(apn_config_avps[0].ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(apn_config_avps[0].ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(apn_config_avps[0].ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(apn_config_avps[0].ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(apn_config_avps[0].ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(apn_config_avps[0].vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(apn_config_avps[0].vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        self.assertEqual(apn_config_avps[0].pdn_gw_allocation_type_avp.code, PDN_GW_ALLOCATION_TYPE_AVP_CODE)
        self.assertEqual(apn_config_avps[0].pdn_gw_allocation_type_avp.data, PDN_GW_ALLOCATION_TYPE_DYNAMIC)
        self.assertEqual(apn_config_avps[0].mip6_agent_info_avp.code, MIP6_AGENT_INFO_AVP_CODE)
        self.assertEqual(apn_config_avps[0].mip6_agent_info_avp.mip_home_agent_host_avp.code, MIP_HOME_AGENT_HOST_AVP_CODE)
        self.assertEqual(apn_config_avps[0].mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.code, DESTINATION_REALM_AVP_CODE)
        self.assertEqual(apn_config_avps[0].mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.data, b"epc.mncXXX.mccYYY.3gppnetwork.org")
        self.assertEqual(apn_config_avps[0].mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.code, DESTINATION_HOST_AVP_CODE)
        self.assertEqual(apn_config_avps[0].mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.data, b"topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")

        self.assertEqual(apn_config_avps[1].code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(apn_config_avps[1].context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(apn_config_avps[1].context_identifier_avp.data, convert_to_4_bytes(4))
        self.assertEqual(apn_config_avps[1].service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(apn_config_avps[1].service_selection_avp.data, b"mms")
        self.assertEqual(apn_config_avps[1].pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(apn_config_avps[1].pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(apn_config_avps[1].eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(apn_config_avps[1].eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(apn_config_avps[1].eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(apn_config_avps[1].eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(apn_config_avps[1].eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(apn_config_avps[1].eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(apn_config_avps[1].ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(apn_config_avps[1].ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(apn_config_avps[1].ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(apn_config_avps[1].ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(apn_config_avps[1].ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(apn_config_avps[1].vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(apn_config_avps[1].vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        self.assertEqual(apn_config_avps[1].pdn_gw_allocation_type_avp.code, PDN_GW_ALLOCATION_TYPE_AVP_CODE)
        self.assertEqual(apn_config_avps[1].pdn_gw_allocation_type_avp.data, PDN_GW_ALLOCATION_TYPE_DYNAMIC)
        self.assertEqual(apn_config_avps[1].mip6_agent_info_avp.code, MIP6_AGENT_INFO_AVP_CODE)
        self.assertEqual(apn_config_avps[1].mip6_agent_info_avp.mip_home_agent_host_avp.code, MIP_HOME_AGENT_HOST_AVP_CODE)
        self.assertEqual(apn_config_avps[1].mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.code, DESTINATION_REALM_AVP_CODE)
        self.assertEqual(apn_config_avps[1].mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.data, b"epc.mncXXX.mccYYY.3gppnetwork.org")
        self.assertEqual(apn_config_avps[1].mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.code, DESTINATION_HOST_AVP_CODE)
        self.assertEqual(apn_config_avps[1].mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.data, b"topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")

        self.assertEqual(apn_config_avps[2].code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(apn_config_avps[2].context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(apn_config_avps[2].context_identifier_avp.data, convert_to_4_bytes(3))
        self.assertEqual(apn_config_avps[2].service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(apn_config_avps[2].service_selection_avp.data, b"xcap")
        self.assertEqual(apn_config_avps[2].pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(apn_config_avps[2].pdn_type_avp.data, PDN_TYPE_IPV6)
        self.assertEqual(apn_config_avps[2].eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(apn_config_avps[2].eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(apn_config_avps[2].eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(apn_config_avps[2].eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(apn_config_avps[2].eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(apn_config_avps[2].eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(apn_config_avps[2].ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(apn_config_avps[2].ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(apn_config_avps[2].ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(apn_config_avps[2].ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(apn_config_avps[2].ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(apn_config_avps[2].vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(apn_config_avps[2].vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        self.assertEqual(apn_config_avps[2].pdn_gw_allocation_type_avp.code, PDN_GW_ALLOCATION_TYPE_AVP_CODE)
        self.assertEqual(apn_config_avps[2].pdn_gw_allocation_type_avp.data, PDN_GW_ALLOCATION_TYPE_DYNAMIC)
        self.assertEqual(apn_config_avps[2].mip6_agent_info_avp.code, MIP6_AGENT_INFO_AVP_CODE)
        self.assertEqual(apn_config_avps[2].mip6_agent_info_avp.mip_home_agent_host_avp.code, MIP_HOME_AGENT_HOST_AVP_CODE)
        self.assertEqual(apn_config_avps[2].mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.code, DESTINATION_REALM_AVP_CODE)
        self.assertEqual(apn_config_avps[2].mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.data, b"epc.mncXXX.mccYYY.3gppnetwork.org")
        self.assertEqual(apn_config_avps[2].mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.code, DESTINATION_HOST_AVP_CODE)
        self.assertEqual(apn_config_avps[2].mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.data, b"topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")

        self.assertEqual(apn_config_avps[3].code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(apn_config_avps[3].context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(apn_config_avps[3].context_identifier_avp.data, convert_to_4_bytes(824))
        self.assertEqual(apn_config_avps[3].service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(apn_config_avps[3].service_selection_avp.data, b"ims")
        self.assertEqual(apn_config_avps[3].pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(apn_config_avps[3].pdn_type_avp.data, PDN_TYPE_IPV4V6)
        self.assertEqual(apn_config_avps[3].eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(apn_config_avps[3].eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(apn_config_avps[3].eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(5))
        self.assertEqual(apn_config_avps[3].eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(apn_config_avps[3].eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(apn_config_avps[3].eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(apn_config_avps[3].ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(apn_config_avps[3].ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(apn_config_avps[3].ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(apn_config_avps[3].ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(apn_config_avps[3].ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(apn_config_avps[3].vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(apn_config_avps[3].vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        self.assertEqual(apn_config_avps[3].pdn_gw_allocation_type_avp.code, PDN_GW_ALLOCATION_TYPE_AVP_CODE)
        self.assertEqual(apn_config_avps[3].pdn_gw_allocation_type_avp.data, PDN_GW_ALLOCATION_TYPE_DYNAMIC)
        self.assertEqual(apn_config_avps[3].mip6_agent_info_avp.code, MIP6_AGENT_INFO_AVP_CODE)
        self.assertEqual(apn_config_avps[3].mip6_agent_info_avp.mip_home_agent_host_avp.code, MIP_HOME_AGENT_HOST_AVP_CODE)
        self.assertEqual(apn_config_avps[3].mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.code, DESTINATION_REALM_AVP_CODE)
        self.assertEqual(apn_config_avps[3].mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.data, b"epc.mncXXX.mccYYY.3gppnetwork.org")
        self.assertEqual(apn_config_avps[3].mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.code, DESTINATION_HOST_AVP_CODE)
        self.assertEqual(apn_config_avps[3].mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.data, b"topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")


class TestGetSubscriberStatus(unittest.TestCase):
    def test__get_subscriber_status__odb_none(self):
        status = get_subscriber_status(odb=None)

        self.assertEqual(status[0].code, SUBSCRIBER_STATUS_AVP_CODE)
        self.assertEqual(status[0].vendor_id, VENDOR_ID_3GPP)
        self.assertEqual(status[0].data, SUBSCRIBER_STATUS_SERVICE_GRANTED)

    def test__get_subscriber_status__odb_all_apn(self):
        status = get_subscriber_status(odb="ODB-all-APN")

        self.assertEqual(status[0].code, SUBSCRIBER_STATUS_AVP_CODE)
        self.assertEqual(status[0].vendor_id, VENDOR_ID_3GPP)
        self.assertEqual(status[0].data, SUBSCRIBER_STATUS_OPERATOR_DETERMINED_BARRING)

        self.assertEqual(status[1].code, OPERATOR_DETERMINED_BARRING_AVP_CODE)
        self.assertEqual(status[1].vendor_id, VENDOR_ID_3GPP)
        self.assertTrue(status[1].is_bit_set(0))
        self.assertFalse(status[1].is_bit_set(1))
        self.assertFalse(status[1].is_bit_set(2))

    def test__get_subscriber_status__odb_hplmn_apn(self):
        status = get_subscriber_status(odb="ODB-HPLMN-APN")

        self.assertEqual(status[0].code, SUBSCRIBER_STATUS_AVP_CODE)
        self.assertEqual(status[0].vendor_id, VENDOR_ID_3GPP)
        self.assertEqual(status[0].data, SUBSCRIBER_STATUS_OPERATOR_DETERMINED_BARRING)

        self.assertEqual(status[1].code, OPERATOR_DETERMINED_BARRING_AVP_CODE)
        self.assertEqual(status[1].vendor_id, VENDOR_ID_3GPP)
        self.assertFalse(status[1].is_bit_set(0))
        self.assertTrue(status[1].is_bit_set(1))
        self.assertFalse(status[1].is_bit_set(2))

    def test__get_subscriber_status__odb_vplmn_apn(self):
        status = get_subscriber_status(odb="ODB-VPLMN-APN")

        self.assertEqual(status[0].code, SUBSCRIBER_STATUS_AVP_CODE)
        self.assertEqual(status[0].vendor_id, VENDOR_ID_3GPP)
        self.assertEqual(status[0].data, SUBSCRIBER_STATUS_OPERATOR_DETERMINED_BARRING)

        self.assertEqual(status[1].code, OPERATOR_DETERMINED_BARRING_AVP_CODE)
        self.assertEqual(status[1].vendor_id, VENDOR_ID_3GPP)
        self.assertFalse(status[1].is_bit_set(0))
        self.assertFalse(status[1].is_bit_set(1))
        self.assertTrue(status[1].is_bit_set(2))


class TestGetSchar(unittest.TestCase):
    def test__get_schar__invalid(self):
        with self.assertRaises(ValueError) as cm:
            schar = get_schar(824)
        
        self.assertEqual(cm.exception.args[0], "Invalid Charging Characteristics value")

    def test__get_schar__1(self):
        self.assertEqual(get_schar(1), bytes.fromhex("30313030"))

    def test__get_schar__2(self):
        self.assertEqual(get_schar(2), bytes.fromhex("30323030"))

    def test__get_schar__3(self):
        self.assertEqual(get_schar(3), bytes.fromhex("30333030"))

    def test__get_schar__4(self):
        self.assertEqual(get_schar(4), bytes.fromhex("30343030"))

    def test__get_schar__5(self):
        self.assertEqual(get_schar(5), bytes.fromhex("30353030"))

    def test__get_schar__6(self):
        self.assertEqual(get_schar(6), bytes.fromhex("30363030"))

    def test__get_schar__7(self):
        self.assertEqual(get_schar(7), bytes.fromhex("30373030"))

    def test__get_schar__8(self):
        self.assertEqual(get_schar(8), bytes.fromhex("30383030"))

    def test__get_schar__9(self):
        self.assertEqual(get_schar(9), bytes.fromhex("30393030"))

    def test__get_schar__10(self):
        self.assertEqual(get_schar(10), bytes.fromhex("30613030"))

    def test__get_schar__11(self):
        self.assertEqual(get_schar(11), bytes.fromhex("30623030"))

    def test__get_schar__12(self):
        self.assertEqual(get_schar(12), bytes.fromhex("30633030"))

    def test__get_schar__13(self):
        self.assertEqual(get_schar(13), bytes.fromhex("30643030"))

    def test__get_schar__14(self):
        self.assertEqual(get_schar(14), bytes.fromhex("30653030"))

    def test__get_schar__15(self):
        self.assertEqual(get_schar(15), bytes.fromhex("30663030"))


class TestCreateSubscriptionData(unittest.TestCase):
    def setUp(self):
        self.Mip6 = namedtuple("Mip6s", ["context_id", "service_selection", "destination_realm", "destination_host"])
        self.Subscriber = namedtuple("Subscriber", ["msisdn", "stn_sr", "odb", "schar", "max_req_bw_ul", "max_req_bw_dl", "default_apn", "apns", "mip6s"])
        self.Apn = namedtuple("Apns", ["apn_id", "apn_name", "pdn_type", "qci", "priority_level", "max_req_bw_dl", "max_req_bw_ul"])

    def test__create_subscription_data__1(self):
        subs = {
            "msisdn": 5521000000001,
            "stn_sr": 5500599999999,
            "odb": None,
            "schar": 8,
            "max_req_bw_ul": 256,
            "max_req_bw_dl": 256,
            "default_apn": 824,
            "apns": [
                self.Apn(apn_id=1, apn_name="internet", pdn_type="IPv4", qci=9, priority_level=8, max_req_bw_dl=999999999, max_req_bw_ul=999999999),
                self.Apn(apn_id=4, apn_name="mms", pdn_type="IPv4", qci=9, priority_level=8, max_req_bw_dl=256, max_req_bw_ul=256),
                self.Apn(apn_id=3, apn_name="xcap", pdn_type="IPv6", qci=9, priority_level=8, max_req_bw_dl=256, max_req_bw_ul=256),
                self.Apn(apn_id=824, apn_name="ims", pdn_type="IPv4v6", qci=5, priority_level=8, max_req_bw_dl=256, max_req_bw_ul=256),
            ],
            "mip6s": [
                self.Mip6(context_id=1, service_selection="internet", destination_realm="epc.mncXXX.mccYYY.3gppnetwork.org", destination_host="topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org"),
                self.Mip6(context_id=4, service_selection="mms", destination_realm="epc.mncXXX.mccYYY.3gppnetwork.org", destination_host="topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org"),
                self.Mip6(context_id=3, service_selection="xcap", destination_realm="epc.mncXXX.mccYYY.3gppnetwork.org", destination_host="topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org"),
                self.Mip6(context_id=824, service_selection="ims", destination_realm="epc.mncXXX.mccYYY.3gppnetwork.org", destination_host="topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org"),
            ]
        }
        subscriber = self.Subscriber(**subs)

        subscription_data = create_subscription_data(subscriber)

        self.assertTrue(isinstance(subscription_data, list))
        self.assertEqual(len(subscription_data), 6)

        self.assertEqual(subscription_data[0].code, MSISDN_AVP_CODE)
        self.assertEqual(subscription_data[0].data, bytes.fromhex("551200000000f1"))

        self.assertEqual(subscription_data[1].code, STN_SR_AVP_CODE)
        self.assertEqual(subscription_data[1].data, bytes.fromhex("550095999999f9"))

        self.assertEqual(subscription_data[2].code, SUBSCRIBER_STATUS_AVP_CODE)
        self.assertEqual(subscription_data[2].data, SUBSCRIBER_STATUS_SERVICE_GRANTED)

        self.assertEqual(subscription_data[3].code, X_3GPP_CHARGING_CHARACTERISTICS_AVP_CODE)
        self.assertEqual(subscription_data[3].data, bytes.fromhex("30383030"))

        self.assertEqual(subscription_data[4].code, AMBR_AVP_CODE)
        self.assertEqual(subscription_data[4].data, bytes.fromhex("00000204c0000010000028af0000010000000203c0000010000028af00000100"))
        self.assertEqual(subscription_data[4].max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(subscription_data[4].max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(subscription_data[4].max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(subscription_data[4].max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))

        self.assertEqual(subscription_data[5].code, APN_CONFIGURATION_PROFILE_AVP_CODE)
        self.assertEqual(subscription_data[5].context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].context_identifier_avp.data, convert_to_4_bytes(824))
        self.assertEqual(subscription_data[5].all_apn_configurations_included_indicator_avp.code, ALL_APN_CONFIGURATIONS_INCLUDED_INDICATOR_AVP_CODE)
        self.assertEqual(subscription_data[5].all_apn_configurations_included_indicator_avp.data, ALL_APN_CONFIGURATIONS_INCLUDED)
        self.assertEqual(subscription_data[5].apn_configuration_avp.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.context_identifier_avp.data, convert_to_4_bytes(1))
        self.assertEqual(subscription_data[5].apn_configuration_avp.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.service_selection_avp.data, b"internet")
        self.assertEqual(subscription_data[5].apn_configuration_avp.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(subscription_data[5].apn_configuration_avp.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        self.assertEqual(subscription_data[5].apn_configuration_avp.pdn_gw_allocation_type_avp.code, PDN_GW_ALLOCATION_TYPE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.pdn_gw_allocation_type_avp.data, PDN_GW_ALLOCATION_TYPE_DYNAMIC)
        self.assertEqual(subscription_data[5].apn_configuration_avp.mip6_agent_info_avp.code, MIP6_AGENT_INFO_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.code, MIP_HOME_AGENT_HOST_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.code, DESTINATION_REALM_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.data, b"epc.mncXXX.mccYYY.3gppnetwork.org")
        self.assertEqual(subscription_data[5].apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.code, DESTINATION_HOST_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.data, b"topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")

        self.assertEqual(subscription_data[5].apn_configuration_avp__1.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.context_identifier_avp.data, convert_to_4_bytes(4))
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.service_selection_avp.data, b"mms")
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.pdn_gw_allocation_type_avp.code, PDN_GW_ALLOCATION_TYPE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.pdn_gw_allocation_type_avp.data, PDN_GW_ALLOCATION_TYPE_DYNAMIC)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.mip6_agent_info_avp.code, MIP6_AGENT_INFO_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.mip6_agent_info_avp.mip_home_agent_host_avp.code, MIP_HOME_AGENT_HOST_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.code, DESTINATION_REALM_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.data, b"epc.mncXXX.mccYYY.3gppnetwork.org")
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.code, DESTINATION_HOST_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.data, b"topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")

        self.assertEqual(subscription_data[5].apn_configuration_avp__2.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.context_identifier_avp.data, convert_to_4_bytes(3))
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.service_selection_avp.data, b"xcap")
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.pdn_type_avp.data, PDN_TYPE_IPV6)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.pdn_gw_allocation_type_avp.code, PDN_GW_ALLOCATION_TYPE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.pdn_gw_allocation_type_avp.data, PDN_GW_ALLOCATION_TYPE_DYNAMIC)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.mip6_agent_info_avp.code, MIP6_AGENT_INFO_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.mip6_agent_info_avp.mip_home_agent_host_avp.code, MIP_HOME_AGENT_HOST_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.code, DESTINATION_REALM_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.data, b"epc.mncXXX.mccYYY.3gppnetwork.org")
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.code, DESTINATION_HOST_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__2.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.data, b"topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")

        self.assertEqual(subscription_data[5].apn_configuration_avp__3.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.context_identifier_avp.data, convert_to_4_bytes(824))
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.service_selection_avp.data, b"ims")
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.pdn_type_avp.data, PDN_TYPE_IPV4V6)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(5))
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.pdn_gw_allocation_type_avp.code, PDN_GW_ALLOCATION_TYPE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.pdn_gw_allocation_type_avp.data, PDN_GW_ALLOCATION_TYPE_DYNAMIC)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.mip6_agent_info_avp.code, MIP6_AGENT_INFO_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.mip6_agent_info_avp.mip_home_agent_host_avp.code, MIP_HOME_AGENT_HOST_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.code, DESTINATION_REALM_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.data, b"epc.mncXXX.mccYYY.3gppnetwork.org")
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.code, DESTINATION_HOST_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__3.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.data, b"topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")

    def test__create_subscription_data__2(self):
        subs = {
            "msisdn": 5521000000001,
            "stn_sr": 5500599999999,
            "odb": None,
            "schar": 8,
            "max_req_bw_ul": 256,
            "max_req_bw_dl": 256,
            "default_apn": 824,
            "apns": [
                self.Apn(apn_id=1, apn_name="internet", pdn_type="IPv4", qci=9, priority_level=8, max_req_bw_dl=999999999, max_req_bw_ul=999999999),
                self.Apn(apn_id=824, apn_name="ims", pdn_type="IPv4v6", qci=5, priority_level=8, max_req_bw_dl=256, max_req_bw_ul=256),
            ],
            "mip6s": [
                self.Mip6(context_id=1, service_selection="internet", destination_realm=None, destination_host=None),
                self.Mip6(context_id=824, service_selection="ims", destination_realm="epc.mncXXX.mccYYY.3gppnetwork.org", destination_host="topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org"),
            ]
        }
        subscriber = self.Subscriber(**subs)

        subscription_data = create_subscription_data(subscriber)

        self.assertTrue(isinstance(subscription_data, list))
        self.assertEqual(len(subscription_data), 6)

        self.assertEqual(subscription_data[0].code, MSISDN_AVP_CODE)
        self.assertEqual(subscription_data[0].data, bytes.fromhex("551200000000f1"))

        self.assertEqual(subscription_data[1].code, STN_SR_AVP_CODE)
        self.assertEqual(subscription_data[1].data, bytes.fromhex("550095999999f9"))

        self.assertEqual(subscription_data[2].code, SUBSCRIBER_STATUS_AVP_CODE)
        self.assertEqual(subscription_data[2].data, SUBSCRIBER_STATUS_SERVICE_GRANTED)

        self.assertEqual(subscription_data[3].code, X_3GPP_CHARGING_CHARACTERISTICS_AVP_CODE)
        self.assertEqual(subscription_data[3].data, bytes.fromhex("30383030"))

        self.assertEqual(subscription_data[4].code, AMBR_AVP_CODE)
        self.assertEqual(subscription_data[4].data, bytes.fromhex("00000204c0000010000028af0000010000000203c0000010000028af00000100"))
        self.assertEqual(subscription_data[4].max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(subscription_data[4].max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(subscription_data[4].max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(subscription_data[4].max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))

        self.assertEqual(subscription_data[5].code, APN_CONFIGURATION_PROFILE_AVP_CODE)
        self.assertEqual(subscription_data[5].context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].context_identifier_avp.data, convert_to_4_bytes(824))
        self.assertEqual(subscription_data[5].all_apn_configurations_included_indicator_avp.code, ALL_APN_CONFIGURATIONS_INCLUDED_INDICATOR_AVP_CODE)
        self.assertEqual(subscription_data[5].all_apn_configurations_included_indicator_avp.data, ALL_APN_CONFIGURATIONS_INCLUDED)
        self.assertEqual(subscription_data[5].apn_configuration_avp.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.context_identifier_avp.data, convert_to_4_bytes(1))
        self.assertEqual(subscription_data[5].apn_configuration_avp.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.service_selection_avp.data, b"internet")
        self.assertEqual(subscription_data[5].apn_configuration_avp.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(subscription_data[5].apn_configuration_avp.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        self.assertFalse(subscription_data[5].apn_configuration_avp.has_avp("pdn_gw_allocation_type_avp"))
        self.assertFalse(subscription_data[5].apn_configuration_avp.has_avp("mip6_agent_info_avp"))
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.context_identifier_avp.data, convert_to_4_bytes(824))
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.service_selection_avp.data, b"ims")
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.pdn_type_avp.data, PDN_TYPE_IPV4V6)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(5))
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.pdn_gw_allocation_type_avp.code, PDN_GW_ALLOCATION_TYPE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.pdn_gw_allocation_type_avp.data, PDN_GW_ALLOCATION_TYPE_DYNAMIC)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.mip6_agent_info_avp.code, MIP6_AGENT_INFO_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.mip6_agent_info_avp.mip_home_agent_host_avp.code, MIP_HOME_AGENT_HOST_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.code, DESTINATION_REALM_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.mip6_agent_info_avp.mip_home_agent_host_avp.destination_realm_avp.data, b"epc.mncXXX.mccYYY.3gppnetwork.org")
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.code, DESTINATION_HOST_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp__1.mip6_agent_info_avp.mip_home_agent_host_avp.destination_host_avp.data, b"topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")

    def test__create_subscription_data__3(self):
        subs = {
            "msisdn": 5521000000001,
            "stn_sr": 5500599999999,
            "odb": None,
            "schar": 8,
            "max_req_bw_ul": 256,
            "max_req_bw_dl": 256,
            "default_apn": 824,
            "apns": [
                self.Apn(apn_id=1, apn_name="internet", pdn_type="IPv4", qci=9, priority_level=8, max_req_bw_dl=999999999, max_req_bw_ul=999999999),
            ],
            "mip6s": [
                self.Mip6(context_id=1, service_selection="internet", destination_realm=None, destination_host=None),
            ]
        }
        subscriber = self.Subscriber(**subs)

        subscription_data = create_subscription_data(subscriber)

        self.assertTrue(isinstance(subscription_data, list))
        self.assertEqual(len(subscription_data), 6)

        self.assertEqual(subscription_data[0].code, MSISDN_AVP_CODE)
        self.assertEqual(subscription_data[0].data, bytes.fromhex("551200000000f1"))

        self.assertEqual(subscription_data[1].code, STN_SR_AVP_CODE)
        self.assertEqual(subscription_data[1].data, bytes.fromhex("550095999999f9"))

        self.assertEqual(subscription_data[2].code, SUBSCRIBER_STATUS_AVP_CODE)
        self.assertEqual(subscription_data[2].data, SUBSCRIBER_STATUS_SERVICE_GRANTED)

        self.assertEqual(subscription_data[3].code, X_3GPP_CHARGING_CHARACTERISTICS_AVP_CODE)
        self.assertEqual(subscription_data[3].data, bytes.fromhex("30383030"))

        self.assertEqual(subscription_data[4].code, AMBR_AVP_CODE)
        self.assertEqual(subscription_data[4].data, bytes.fromhex("00000204c0000010000028af0000010000000203c0000010000028af00000100"))
        self.assertEqual(subscription_data[4].max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(subscription_data[4].max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(subscription_data[4].max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(subscription_data[4].max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))

        self.assertEqual(subscription_data[5].code, APN_CONFIGURATION_PROFILE_AVP_CODE)
        self.assertEqual(subscription_data[5].context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].context_identifier_avp.data, convert_to_4_bytes(824))
        self.assertEqual(subscription_data[5].all_apn_configurations_included_indicator_avp.code, ALL_APN_CONFIGURATIONS_INCLUDED_INDICATOR_AVP_CODE)
        self.assertEqual(subscription_data[5].all_apn_configurations_included_indicator_avp.data, ALL_APN_CONFIGURATIONS_INCLUDED)
        self.assertEqual(subscription_data[5].apn_configuration_avp.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.context_identifier_avp.data, convert_to_4_bytes(1))
        self.assertEqual(subscription_data[5].apn_configuration_avp.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.service_selection_avp.data, b"internet")
        self.assertEqual(subscription_data[5].apn_configuration_avp.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(subscription_data[5].apn_configuration_avp.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        self.assertFalse(subscription_data[5].apn_configuration_avp.has_avp("pdn_gw_allocation_type_avp"))
        self.assertFalse(subscription_data[5].apn_configuration_avp.has_avp("mip6_agent_info_avp"))

    def test__create_subscription_data__3(self):
        subs = {
            "msisdn": 5521000000005,
            "stn_sr": 5500599999999,
            "odb": None,
            "schar": 8,
            "max_req_bw_ul": 256,
            "max_req_bw_dl": 256,
            "default_apn": 824,
            "apns": [
                self.Apn(apn_id=1, apn_name="internet", pdn_type="IPv4", qci=9, priority_level=8, max_req_bw_dl=999999999, max_req_bw_ul=999999999),
            ],
            "mip6s": [
                self.Mip6(context_id=1, service_selection="internet", destination_realm=None, destination_host=None),
            ]
        }
        subscriber = self.Subscriber(**subs)

        subscription_data = create_subscription_data(subscriber)

        self.assertTrue(isinstance(subscription_data, list))
        self.assertEqual(len(subscription_data), 6)

        self.assertEqual(subscription_data[0].code, MSISDN_AVP_CODE)
        self.assertEqual(subscription_data[0].data, bytes.fromhex("551200000000f5"))

        self.assertEqual(subscription_data[1].code, STN_SR_AVP_CODE)
        self.assertEqual(subscription_data[1].data, bytes.fromhex("550095999999f9"))

        self.assertEqual(subscription_data[2].code, SUBSCRIBER_STATUS_AVP_CODE)
        self.assertEqual(subscription_data[2].data, SUBSCRIBER_STATUS_SERVICE_GRANTED)

        self.assertEqual(subscription_data[3].code, X_3GPP_CHARGING_CHARACTERISTICS_AVP_CODE)
        self.assertEqual(subscription_data[3].data, bytes.fromhex("30383030"))

        self.assertEqual(subscription_data[4].code, AMBR_AVP_CODE)
        self.assertEqual(subscription_data[4].data, bytes.fromhex("00000204c0000010000028af0000010000000203c0000010000028af00000100"))
        self.assertEqual(subscription_data[4].max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(subscription_data[4].max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(subscription_data[4].max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(subscription_data[4].max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))

        self.assertEqual(subscription_data[5].code, APN_CONFIGURATION_PROFILE_AVP_CODE)
        self.assertEqual(subscription_data[5].context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].context_identifier_avp.data, convert_to_4_bytes(824))
        self.assertEqual(subscription_data[5].all_apn_configurations_included_indicator_avp.code, ALL_APN_CONFIGURATIONS_INCLUDED_INDICATOR_AVP_CODE)
        self.assertEqual(subscription_data[5].all_apn_configurations_included_indicator_avp.data, ALL_APN_CONFIGURATIONS_INCLUDED)
        self.assertEqual(subscription_data[5].apn_configuration_avp.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.context_identifier_avp.data, convert_to_4_bytes(1))
        self.assertEqual(subscription_data[5].apn_configuration_avp.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.service_selection_avp.data, b"internet")
        self.assertEqual(subscription_data[5].apn_configuration_avp.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(subscription_data[5].apn_configuration_avp.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(subscription_data[5].apn_configuration_avp.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)
        self.assertFalse(subscription_data[5].apn_configuration_avp.has_avp("pdn_gw_allocation_type_avp"))
        self.assertFalse(subscription_data[5].apn_configuration_avp.has_avp("mip6_agent_info_avp"))


class TestCreateFeatureListAvp(unittest.TestCase):
    def test__create_feature_list_avp(self):
        feature_list_avp = create_feature_list_avp()

        self.assertEqual(feature_list_avp.code, FEATURE_LIST_AVP_CODE)
        self.assertEqual(feature_list_avp.data, bytes.fromhex("00000007"))


class TestCreateSupportedFeatures(unittest.TestCase):
    def test__create_supported_features(self):
        supported_features = create_supported_features()
        vendor_id_avp, feature_list_id_avp, feature_list_avp = supported_features

        self.assertEqual(vendor_id_avp.code, VENDOR_ID_AVP_CODE)
        self.assertEqual(vendor_id_avp.data, VENDOR_ID_3GPP)

        self.assertEqual(feature_list_id_avp.code, FEATURE_LIST_ID_AVP_CODE)
        self.assertEqual(feature_list_id_avp.data, bytes.fromhex("00000001"))

        self.assertEqual(feature_list_avp.code, FEATURE_LIST_AVP_CODE)
        self.assertEqual(feature_list_avp.data, bytes.fromhex("00000007"))


class TestHasAllowedRat(unittest.TestCase):
    def test__has_allowed_rat__wlan(self):
        ulr_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "rat_type": RAT_TYPE_WLAN,
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                                                            VendorIdAVP(VENDOR_ID_3GPP), 
                                                            AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
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
        ulr = ULR(**ulr_avps)
        self.assertFalse(has_allowed_rat(ulr))

    def test__has_allowed_rat__eutran(self):
        ulr_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "rat_type": RAT_TYPE_EUTRAN,
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                                                            VendorIdAVP(VENDOR_ID_3GPP), 
                                                            AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
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
        ulr = ULR(**ulr_avps)
        self.assertTrue(has_allowed_rat(ulr))

    def test__has_allowed_rat__invalid_value(self):
        ulr_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                                                            VendorIdAVP(VENDOR_ID_3GPP), 
                                                            AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
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
        ulr = ULR(**ulr_avps)
        ulr.pop("rat_type_avp")
        
        with self.assertRaises(DiameterMissingAvp) as cm:
            has_rat = has_allowed_rat(ulr)
            print(has_rat)
        
        self.assertEqual(cm.exception.args[0], "RAT-Type AVP not found")


class TestIsNewMmeIdentity(unittest.TestCase):
    def test__is_new_mme_identity__1(self):
        Subscriber = namedtuple("Subscriber", ["mme_hostname"])
        subscriber = Subscriber("localhost.domain")
        
        nor_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "context_identifier": 3,
                    "service_selection": "internet",
                    "nor_flags": 0x00000000,
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        nor = NOR(**nor_avps)

        self.assertFalse(is_new_mme_identity(nor, subscriber))

    def test__is_new_mme_identity__2(self):
        Subscriber = namedtuple("Subscriber", ["mme_hostname"])
        subscriber = Subscriber("localhost.domain")
        
        nor_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost_1.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "context_identifier": 3,
                    "service_selection": "internet",
                    "nor_flags": 0x00000000,
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        nor = NOR(**nor_avps)

        self.assertTrue(is_new_mme_identity(nor, subscriber))

    def test__is_new_mme_identity__3(self):
        Subscriber = namedtuple("Subscriber", ["mme_hostname"])
        subscriber = Subscriber(None)
        
        nor_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "context_identifier": 3,
                    "service_selection": "internet",
                    "nor_flags": 0x00000000,
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        nor = NOR(**nor_avps)

        self.assertFalse(is_new_mme_identity(nor, subscriber))


class TestGetContextId(unittest.TestCase):
    def test__get_context_id__valid(self):
        nor_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "context_identifier": 3,
                    "service_selection": "internet",
                    "nor_flags": 0x00000000,
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        nor = NOR(**nor_avps)

        context_id = get_context_id(nor)
        self.assertEqual(context_id, 3)

    def test__get_context_id__invalid(self):
        nor_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "service_selection": "internet",
                    "nor_flags": 0x00000000,
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        nor = NOR(**nor_avps)

        with self.assertRaises(DiameterMissingAvp) as cm:
            context_id = get_context_id(nor)
        
        self.assertEqual(cm.exception.args[0], "Context-Identifier AVP not found")


class TestGetServiceSelection(unittest.TestCase):
    def test__get_service_selection__valid(self):
        nor_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "context_identifier": 3,
                    "service_selection": "internet",
                    "nor_flags": 0x00000000,
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        nor = NOR(**nor_avps)

        service_selection = get_service_selection(nor)
        self.assertEqual(service_selection, "internet")

    def test__get_service_selection__invalid(self):
        nor_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "nor_flags": 0x00000000,
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        nor = NOR(**nor_avps)

        with self.assertRaises(DiameterMissingAvp) as cm:
            service_selection = get_service_selection(nor)
        
        self.assertEqual(cm.exception.args[0], "Service-Selection AVP not found")


class TestGetMip6AgentHostDestinationHost(unittest.TestCase):
    def test__get_mip6_agent_host_destination_host__valid(self):
        nor_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "context_identifier": 3,
                    "service_selection": "internet",
                    "nor_flags": 0x00000000,
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        nor = NOR(**nor_avps)

        destination_host = get_mip6_agent_host_destination_host(nor)
        self.assertEqual(destination_host, "topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")

    def test__get_mip6_agent_host_destination_host__invalid__no_destination_host(self):
        nor_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "nor_flags": 0x00000000,
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        nor = NOR(**nor_avps)

        nor.mip6_agent_info_avp.mip_home_agent_host_avp.pop("destination_host_avp")
        nor.refresh()

        with self.assertRaises(DiameterMissingAvp) as cm:
            destination_host = get_mip6_agent_host_destination_host(nor)
        
        self.assertEqual(cm.exception.args[0], "Destination-Host AVP not found")

    def test__get_mip6_agent_host_destination_host__invalid__no_mip_home_agent_host(self):
        nor_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "nor_flags": 0x00000000,
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        nor = NOR(**nor_avps)

        nor.mip6_agent_info_avp.pop("mip_home_agent_host_avp")
        nor.refresh()

        with self.assertRaises(DiameterMissingAvp) as cm:
            destination_host = get_mip6_agent_host_destination_host(nor)
        
        self.assertEqual(cm.exception.args[0], "MIP-Home-Agent-Host AVP not found")

    def test__get_mip6_agent_host_destination_host__invalid__no_mip6_agent_info(self):
        nor_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "nor_flags": 0x00000000,
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        nor = NOR(**nor_avps)

        nor.pop("mip6_agent_info_avp")
        nor.refresh()

        with self.assertRaises(DiameterMissingAvp) as cm:
            destination_host = get_mip6_agent_host_destination_host(nor)
        
        self.assertEqual(cm.exception.args[0], "MIP6-Agent-Info AVP not found")


class TestGetMip6AgentHostDestinationRealm(unittest.TestCase):
    def test__get_mip6_agent_host_destination_realm__valid(self):
        nor_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "context_identifier": 3,
                    "service_selection": "internet",
                    "nor_flags": 0x00000000,
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        nor = NOR(**nor_avps)

        destination_realm = get_mip6_agent_host_destination_realm(nor)
        self.assertEqual(destination_realm, "epc.mncXXX.mccYYY.3gppnetwork.org")

    def test__get_mip6_agent_host_destination_realm__invalid__no_destination_host(self):
        nor_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "nor_flags": 0x00000000,
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        nor = NOR(**nor_avps)

        nor.mip6_agent_info_avp.mip_home_agent_host_avp.pop("destination_realm_avp")
        nor.refresh()

        with self.assertRaises(DiameterMissingAvp) as cm:
            destination_realm = get_mip6_agent_host_destination_realm(nor)
        
        self.assertEqual(cm.exception.args[0], "Destination-Realm AVP not found")

    def test__get_mip6_agent_host_destination_realm__invalid__no_mip_home_agent_host(self):
        nor_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "nor_flags": 0x00000000,
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        nor = NOR(**nor_avps)

        nor.mip6_agent_info_avp.pop("mip_home_agent_host_avp")
        nor.refresh()

        with self.assertRaises(DiameterMissingAvp) as cm:
            destination_realm = get_mip6_agent_host_destination_realm(nor)
        
        self.assertEqual(cm.exception.args[0], "MIP-Home-Agent-Host AVP not found")

    def test__get_mip6_agent_host_destination_realm__invalid__no_mip6_agent_info(self):
        nor_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "nor_flags": 0x00000000,
                    "mip6_agent_info": [MipHomeAgentHostAVP([
                                            DestinationRealmAVP("epc.mncXXX.mccYYY.3gppnetwork.org"),
                                            DestinationHostAVP("topon.s5pgw.node.epc.mncXXX.mccYYY.3gppnetwork.org")
                    ])]
        }
        nor = NOR(**nor_avps)

        nor.pop("mip6_agent_info_avp")
        nor.refresh()

        with self.assertRaises(DiameterMissingAvp) as cm:
            destination_realm = get_mip6_agent_host_destination_realm(nor)
        
        self.assertEqual(cm.exception.args[0], "MIP6-Agent-Info AVP not found")


class TestDecodeFromPlmn(unittest.TestCase):
    def test__decode_from_plmn__1__72405(self):
        plmn = bytes.fromhex("27f450")
        mcc, mnc = decode_from_plmn(plmn)

        self.assertEqual(mcc, 724)
        self.assertEqual(mnc, 5)
        self.assertEqual(encode_to_plmn(mcc, mnc), plmn)

    def test__decode_from_plmn__2__21401(self):
        plmn = bytes.fromhex("12f410")
        mcc, mnc = decode_from_plmn(plmn)

        self.assertEqual(mcc, 214)
        self.assertEqual(mnc, 1)
        self.assertEqual(encode_to_plmn(mcc, mnc), plmn)

    def test__decode_from_plmn__3__50593(self):
        plmn = bytes.fromhex("05f539")
        mcc, mnc = decode_from_plmn(plmn)

        self.assertEqual(mcc, 505)
        self.assertEqual(mnc, 93)
        self.assertEqual(encode_to_plmn(mcc, mnc), plmn)

    def test__decode_from_plmn__4__90170(self):
        plmn = bytes.fromhex("09f107")
        mcc, mnc = decode_from_plmn(plmn)

        self.assertEqual(mcc, 901)
        self.assertEqual(mnc, 70)
        self.assertEqual(encode_to_plmn(mcc, mnc), plmn)


class TestEncodeToPlmn(unittest.TestCase):
    def test__encode_to_plmn__1__72405(self):
        self.assertEqual(encode_to_plmn(724, 5), bytes.fromhex("27f450"))

    def test__decode_from_plmn__2__21401(self):
        self.assertEqual(encode_to_plmn(214, 1), bytes.fromhex("12f410"))

    def test__decode_from_plmn__3__50593(self):
        self.assertEqual(encode_to_plmn(505, 93), bytes.fromhex("05f539"))

    def test__decode_from_plmn__4__90170(self):
        self.assertEqual(encode_to_plmn(901, 70), bytes.fromhex("09f107"))


class TestIs3gppRealmFormat(unittest.TestCase):
    def test__is_3gpp_realm_format__valid__72405(self):
        self.assertTrue(is_3gpp_realm_format("epc.mnc005.mcc724.3gppnetwork.org"))

    def test__is_3gpp_realm_format__valid__21401(self):
        self.assertTrue(is_3gpp_realm_format("epc.mnc001.mcc214.3gppnetwork.org"))

    def test__is_3gpp_realm_format__valid__50593(self):
        self.assertTrue(is_3gpp_realm_format("epc.mnc093.mcc505.3gppnetwork.org"))

    def test__is_3gpp_realm_format__valid__90170(self):
        self.assertTrue(is_3gpp_realm_format("epc.mnc070.mcc901.3gppnetwork.org"))

    def test__is_3gpp_realm_format__invalid__72405(self):
        self.assertFalse(is_3gpp_realm_format("epc.mnc5.mcc724.3gppnetwork.org"))

    def test__is_3gpp_realm_format__invalid__21401(self):
        self.assertFalse(is_3gpp_realm_format("epc.mnc1.mcc214.3gppnetwork.org"))

    def test__is_3gpp_realm_format__invalid__50593(self):
        self.assertFalse(is_3gpp_realm_format("epc.mnc93.mcc505.3gppnetwork.org"))

    def test__is_3gpp_realm_format__invalid__90170(self):
        self.assertFalse(is_3gpp_realm_format("epc.mnc70.mcc901.3gppnetwork.org"))

    def test__is_3gpp_realm_format__invalid__domain(self):
        self.assertFalse(is_3gpp_realm_format("domain"))


class TestIsSubscriberRoaming(unittest.TestCase):
    def test__is_subscriber_roaming__ulr__same_realm__with_no_check_realm(self):
        ulr_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "rat_type": RAT_TYPE_EUTRAN,
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                                                            VendorIdAVP(VENDOR_ID_3GPP), 
                                                            AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
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
        ulr = ULR(**ulr_avps)

        self.assertFalse(is_subscriber_roaming(ulr))

    def test__is_subscriber_roaming__ulr__same_realm__with_check_realm(self):
        ulr_avps = {
                    "session_id": "localhost.domain",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "domain",
                    "destination_host": "remotehost.domain",
                    "user_name": "999000000000000",
                    "rat_type": RAT_TYPE_EUTRAN,
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                                                            VendorIdAVP(VENDOR_ID_3GPP), 
                                                            AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
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
        ulr = ULR(**ulr_avps)

        self.assertFalse(is_subscriber_roaming(ulr, check_remote_realm=True))

    def test__is_subscriber_roaming__ulr__different_realm__with_no_check_realm(self):
        ulr_avps = {
                    "session_id": "localhost.mnc000.mcc999.3gppnetwork.org",
                    "origin_host": "localhost.mnc000.mcc999.3gppnetwork.org",
                    "origin_realm": "mnc000.mcc999.3gppnetwork.org",
                    "destination_realm": "mnc001.mcc999.3gppnetwork.org",
                    "destination_host": "remotehost.mnc001.mcc999.3gppnetwork.org",
                    "user_name": "999000000000000",
                    "rat_type": RAT_TYPE_EUTRAN,
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                                                            VendorIdAVP(VENDOR_ID_3GPP), 
                                                            AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
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
        ulr = ULR(**ulr_avps)

        self.assertTrue(is_subscriber_roaming(ulr))

    def test__is_subscriber_roaming__ulr__different_realm__with_check_realm(self):
        ulr_avps = {
                    "session_id": "localhost.mnc000.mcc999.3gppnetwork.org",
                    "origin_host": "localhost.mnc000.mcc999.3gppnetwork.org",
                    "origin_realm": "mnc000.mcc999.3gppnetwork.org",
                    "destination_realm": "mnc001.mcc999.3gppnetwork.org",
                    "destination_host": "remotehost.mnc001.mcc999.3gppnetwork.org",
                    "user_name": "999000000000000",
                    "rat_type": RAT_TYPE_EUTRAN,
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                                                            VendorIdAVP(VENDOR_ID_3GPP), 
                                                            AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
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
        ulr = ULR(**ulr_avps)

        self.assertTrue(is_subscriber_roaming(ulr, check_remote_realm=True))

    def test__is_subscriber_roaming__ulr__different_realm_no_3gpp_compliant__with_check_realm(self):
        ulr_avps = {
                    "session_id": "localhost.mnc000.mcc999.3gppnetwork.org",
                    "origin_host": "localhost.domain",
                    "origin_realm": "domain",
                    "destination_realm": "mnc001.mcc999.3gppnetwork.org",
                    "destination_host": "remotehost.mnc001.mcc999.3gppnetwork.org",
                    "user_name": "999000000000000",
                    "rat_type": RAT_TYPE_EUTRAN,
                    "ulr_flags": 3,
                    "visited_plmn_id": bytes.fromhex("09f107"),
                    "vendor_specific_application_id": [
                                                            VendorIdAVP(VENDOR_ID_3GPP), 
                                                            AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
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
        ulr = ULR(**ulr_avps)

        with self.assertRaises(DiameterInvalidAvpValue) as cm:
            is_ = is_subscriber_roaming(ulr, check_remote_realm=True) 

        self.assertEqual(cm.exception.args[0], "Origin-Realm AVP does not comply with 3GPP format: mncMNC.mccMCC.3gppnetwork.org")


class TestCreateMissingAvpResponse(unittest.TestCase):
    def setUp(self):
        basedir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(basedir, "config.yaml")

        app = Bromelia(config_file=config_file)

        #: Application initialization
        msgs = [AIA, AIR, CLA, CLR, NOA, NOR, PUA, PUR, ULA, ULR]
        app.load_messages_into_application_id(msgs, DIAMETER_APPLICATION_S6a_S6d)

        self.aia = app.s6a.AIA
        self.noa = app.s6a.NA
        self.pua = app.s6a.PUA
        self.ula = app.s6a.ULA

    def test__create_missing_avp_response__aia__msg_only(self):
        aia = create_missing_avp_response(proxy_response=self.aia, msg="User-Name AVP not found")

        self.assertEqual(aia.vendor_specific_application_id_avp.code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(aia.vendor_specific_application_id_avp.dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(aia.result_code_avp.code, RESULT_CODE_AVP_CODE)
        self.assertEqual(aia.result_code_avp.dump().hex(), "0000010c4000000c0000138d")
        self.assertEqual(aia.result_code_avp.data, DIAMETER_MISSING_AVP)

        self.assertEqual(aia.auth_session_state_avp.code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(aia.auth_session_state_avp.dump().hex(), "000001154000000c00000001")

        self.assertEqual(aia.origin_host_avp.code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(aia.origin_host_avp.dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.origin_realm_avp.code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(aia.origin_realm_avp.dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.error_message_avp.code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(aia.error_message_avp.dump().hex(), "000001190000001f557365722d4e616d6520415650206e6f7420666f756e6400")
        self.assertEqual(aia.error_message_avp.data, b"User-Name AVP not found")

    def test__create_missing_avp_response__noa__msg_only(self):
        noa = create_missing_avp_response(proxy_response=self.noa, msg="User-Name AVP not found")

        self.assertEqual(noa.vendor_specific_application_id_avp.code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(noa.vendor_specific_application_id_avp.dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(noa.result_code_avp.code, RESULT_CODE_AVP_CODE)
        self.assertEqual(noa.result_code_avp.dump().hex(), "0000010c4000000c0000138d")
        self.assertEqual(noa.result_code_avp.data, DIAMETER_MISSING_AVP)

        self.assertEqual(noa.auth_session_state_avp.code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(noa.auth_session_state_avp.dump().hex(), "000001154000000c00000001")

        self.assertEqual(noa.origin_host_avp.code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(noa.origin_host_avp.dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.origin_realm_avp.code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(noa.origin_realm_avp.dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.error_message_avp.code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(noa.error_message_avp.dump().hex(), "000001190000001f557365722d4e616d6520415650206e6f7420666f756e6400")
        self.assertEqual(noa.error_message_avp.data, b"User-Name AVP not found")

    def test__create_missing_avp_response__pua__msg_only(self):
        pua = create_missing_avp_response(proxy_response=self.pua, msg="User-Name AVP not found")

        self.assertEqual(pua.vendor_specific_application_id_avp.code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(pua.vendor_specific_application_id_avp.dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(pua.result_code_avp.code, RESULT_CODE_AVP_CODE)
        self.assertEqual(pua.result_code_avp.dump().hex(), "0000010c4000000c0000138d")
        self.assertEqual(pua.result_code_avp.data, DIAMETER_MISSING_AVP)

        self.assertEqual(pua.auth_session_state_avp.code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(pua.auth_session_state_avp.dump().hex(), "000001154000000c00000001")

        self.assertEqual(pua.origin_host_avp.code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(pua.origin_host_avp.dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(pua.origin_realm_avp.code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(pua.origin_realm_avp.dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(pua.error_message_avp.code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(pua.error_message_avp.dump().hex(), "000001190000001f557365722d4e616d6520415650206e6f7420666f756e6400")
        self.assertEqual(pua.error_message_avp.data, b"User-Name AVP not found")

    def test__create_missing_avp_response__ula__msg_only(self):
        ula = create_missing_avp_response(proxy_response=self.ula, msg="User-Name AVP not found")

        self.assertEqual(ula.vendor_specific_application_id_avp.code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(ula.vendor_specific_application_id_avp.dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(ula.result_code_avp.code, RESULT_CODE_AVP_CODE)
        self.assertEqual(ula.result_code_avp.dump().hex(), "0000010c4000000c0000138d")
        self.assertEqual(ula.result_code_avp.data, DIAMETER_MISSING_AVP)

        self.assertEqual(ula.auth_session_state_avp.code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(ula.auth_session_state_avp.dump().hex(), "000001154000000c00000001")

        self.assertEqual(ula.origin_host_avp.code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(ula.origin_host_avp.dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.origin_realm_avp.code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(ula.origin_realm_avp.dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.error_message_avp.code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(ula.error_message_avp.dump().hex(), "000001190000001f557365722d4e616d6520415650206e6f7420666f756e6400")
        self.assertEqual(ula.error_message_avp.data, b"User-Name AVP not found")


if __name__ == "__main__":
    unittest.main()