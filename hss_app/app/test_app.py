# -*- coding: utf-8 -*-
"""
    hss_app.test_app
    ~~~~~~~~~~~~~~~~

    This module contains the HSS's core function unittests.
    
    :copyright: (c) 2021 Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

import json
import os
import re
import subprocess
import sys
import unittest


import requests

from bromelia.lib.etsi_3gpp_s6a import *
from bromelia.lib.etsi_3gpp_s6a import AIR # AuthenticationInformationRequest
from bromelia.lib.etsi_3gpp_s6a import CLA # CancelLocationAnswer
from bromelia.lib.etsi_3gpp_s6a import NOR # NotifyRequest
from bromelia.lib.etsi_3gpp_s6a import ULR # UpdateLocationRequest
from bromelia.exceptions import *

app_dir = os.path.dirname(os.path.abspath(__file__))
hss_app_dir = os.path.dirname(app_dir)
bromelia_hss_dir = os.path.dirname(hss_app_dir)

tests_dir = os.path.join(bromelia_hss_dir, "tests")

sys.path.insert(0, tests_dir)

from messages import Air, Nor, Pur, Ulr


def hss_status_ok() -> bool:
    try:
        process = subprocess.Popen(["docker", "container", "ls"], stdout=subprocess.PIPE)
    except FileNotFoundError:
        print(f"[error] command not found: docker")
        return False

    output, err = process.communicate()

    pending_containers = []

    #: Check if hss_app-postgres service is running (as container)
    pattern = re.findall(r"([a-z0-9]{12}).*hss_app-postgres", output.decode("utf-8"))
    if not pattern:
        pending_containers.append("hss_app-postgres")


    #: Check if hss_app-cache container is running (as container)
    pattern = re.findall(r"([a-z0-9]{12}).*hss_app-cache", output.decode("utf-8"))
    if not pattern or "redis" not in output.decode("utf-8"):
        pending_containers.append("hss_app-cache")


    #: Check if hss_app-provisioning_app is running 

    #: (as a container)
    pattern = re.findall(r"([a-z0-9]{12}).*hss_app-provisioning_app", output.decode("utf-8"))

    #: (out of a container)
    output = subprocess.check_output("ps waux | grep entrypoint.py", shell=True)
    processes = output.decode("utf-8").split("\n")

    #: (check)
    print(len(processes))
    if not pattern and len(processes) < 2:
        pending_containers.append("hss_app-provisioning_app")
    

    #: Message in case there is no running needed service
    if pending_containers:
        print(f"[error] Expected container(s) not found: {pending_containers}. Please start the hss_app service")
        return False

    return True


#: Check if main hss_app containers are running, otherwise do not run test cases
if not hss_status_ok():
    sys.exit(0)


from app import *
from counters import app_counterdb as cdb


cdb.flushall()


# @unittest.skip
class TestAirRoute(unittest.TestCase):
    def setUp(self):
        #: Get route function
        self.air = app.get_route("air")

        #: Setup variables to APN creation
        self.base_url_apn = "http://localhost:5001/apns"

        content = {
            "apn_id": 1,
            "apn_name": "internet",
            "pdn_type": "IPv4v6",
            "qci": 9,
            "priority_level": 8,
            "max_req_bw_ul": 999999999,
            "max_req_bw_dl": 999999999
        }

        #: Create APN
        r = requests.post(
            self.base_url_apn, 
            data=json.dumps(content), 
            headers={"Content-Type": "application/json"}
        )

        #: Setup variables to subscriber creation
        self.base_url_subscriber = "http://localhost:5001/subscribers"

        content = {
            "identities": {
                "imsi": "999000000000001",
                "msisdn": "5521000000001"
            },
            "auth": {
                "key": "465b5ce8b199b49faa5f0a2ee238a6bc",
                "opc": "013d7d16d7ad4fefb61bd95b765c8ceb",
                "amf": "b9b9",
                "sqn": "ff9bb4d0b607"
            },
            "subscription": {
                "schar": 8,
                "stn_sr": "5500599999999",
                "odb": "ODB-VPLMN-APN",
                "roaming_allowed": False,
                "max_req_bw_ul": 100000,
                "max_req_bw_dl": 100000,
                "default_apn": 1,
                "apns": [
                    1
                ]
            }
        }

        #: Create Subscriber
        r = requests.post(
            self.base_url_subscriber, 
            data=json.dumps(content), 
            headers={"Content-Type": "application/json"}
        )

    def tearDown(self):
        #: Delete Subscriber
        r = requests.delete(f"{self.base_url_subscriber}/imsi/999000000000001")

        #: Delete APN
        r = requests.delete(f"{self.base_url_apn}/1")

    def test__air_route__0__diameter_missing_user_name_avp(self):
        #: Create Authentication-Information-Request with missing User-Name AVP
        aia = self.air(request=Air.missing_user_name_avp())

        #: Diameter Header
        self.assertEqual(aia.header.version, DIAMETER_VERSION)
        self.assertEqual(aia.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(aia.header.command_code, AUTHENTICATION_INFORMATION_MESSAGE)
        self.assertEqual(aia.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(aia.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(aia.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(aia.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(aia.avps[2].dump().hex(), "0000010c4000000c0000138d")
        self.assertEqual(aia.avps[2].data, DIAMETER_MISSING_AVP)

        self.assertEqual(aia.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(aia.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(aia.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(aia.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(aia.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[6].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(aia.avps[6].dump().hex(), "000001190000001f557365722d4e616d6520415650206e6f7420666f756e6400")
        self.assertEqual(aia.avps[6].data, b"User-Name AVP not found")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("air:num_answers:missing_avp"), b'1')
        cdb.decr("air:num_answers:missing_avp")

        self.assertEqual(cdb.get("air:num_requests"), b'1')
        cdb.decr("air:num_requests")

    def test__air_route__1__diameter_invalid_user_name_avp_value(self):
        #: Create Authentication-Information-Request with invalid User-Name AVP value (less than 15 length digits)
        request = Air.invalid_user_name_avp()
        aia = self.air(request)

        #: Diameter Header
        self.assertEqual(aia.header.version, DIAMETER_VERSION)
        self.assertEqual(aia.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(aia.header.command_code, AUTHENTICATION_INFORMATION_MESSAGE)
        self.assertEqual(aia.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(aia.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(aia.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(aia.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(aia.avps[2].dump().hex(), "0000010c4000000c0000138c")
        self.assertEqual(aia.avps[2].data, DIAMETER_INVALID_AVP_VALUE)

        self.assertEqual(aia.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(aia.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(aia.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(aia.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(aia.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[6].code, FAILED_AVP_AVP_CODE)
        self.assertEqual(aia.avps[6].dump().hex(), "0000011740000020000000014000001539393930303030303030303030000000")
        self.assertEqual(aia.avps[6].user_name_avp, request.user_name_avp)

        self.assertEqual(aia.avps[7].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(aia.avps[7].dump().hex(), "0000011900000027557365722d4e616d65204156502068617320696e76616c69642076616c756500")
        self.assertEqual(aia.avps[7].data, b"User-Name AVP has invalid value")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("air:num_answers:invalid_avp_value"), b'1')
        cdb.decr("air:num_answers:invalid_avp_value")

        self.assertEqual(cdb.get("air:num_requests"), b'1')
        cdb.decr("air:num_requests")

    def test__air_route__2__diameter_missing_visited_plmn_id_avp(self):
        #: Create Authentication-Information-Request with missing Visited-PLMN-Id AVP
        aia = self.air(request=Air.missing_visited_plmn_id_avp())

        #: Diameter Header
        self.assertEqual(aia.header.version, DIAMETER_VERSION)
        self.assertEqual(aia.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(aia.header.command_code, AUTHENTICATION_INFORMATION_MESSAGE)
        self.assertEqual(aia.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(aia.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(aia.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(aia.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(aia.avps[2].dump().hex(), "0000010c4000000c0000138d")
        self.assertEqual(aia.avps[2].data, DIAMETER_MISSING_AVP)

        self.assertEqual(aia.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(aia.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(aia.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(aia.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(aia.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[6].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(aia.avps[6].dump().hex(), "0000011900000025566973697465642d504c4d4e2d496420415650206e6f7420666f756e64000000")
        self.assertEqual(aia.avps[6].data, b"Visited-PLMN-Id AVP not found")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("air:num_answers:missing_avp"), b'1')
        cdb.decr("air:num_answers:missing_avp")

        self.assertEqual(cdb.get("air:num_requests"), b'1')
        cdb.decr("air:num_requests")

    def test__air_route__3__diameter_error_user_unknown(self):
        #: Create Authentication-Information-Request with unknown user
        aia = self.air(request=Air.error_user_unknown())

        #: Diameter Header
        self.assertEqual(aia.header.version, DIAMETER_VERSION)
        self.assertEqual(aia.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(aia.header.command_code, AUTHENTICATION_INFORMATION_MESSAGE)
        self.assertEqual(aia.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(aia.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(aia.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(aia.avps[2].code, EXPERIMENTAL_RESULT_AVP_CODE)
        self.assertEqual(aia.avps[2].dump().hex(), "00000129000000200000012a4000000c000013890000010a4000000c000028af")
        self.assertEqual(aia.avps[2].experimental_result_code_avp.data, DIAMETER_ERROR_USER_UNKNOWN)

        self.assertEqual(aia.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(aia.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(aia.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(aia.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(aia.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("air:num_answers:user_unknown"), b'1')
        cdb.decr("air:num_answers:user_unknown")

        self.assertEqual(cdb.get("air:num_requests"), b'1')
        cdb.decr("air:num_requests")

    def test__air_route__4__diameter_missing_requested_eutran_authentication_info_avp(self):
        #: Create Authentication-Information-Request with missing Requested-EUTRAN-Authentication-Info AVP
        aia = self.air(request=Air.missing_requested_eutran_authentication_info_avp())

        #: Diameter Header
        self.assertEqual(aia.header.version, DIAMETER_VERSION)
        self.assertEqual(aia.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(aia.header.command_code, AUTHENTICATION_INFORMATION_MESSAGE)
        self.assertEqual(aia.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(aia.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(aia.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(aia.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(aia.avps[2].dump().hex(), "0000010c4000000c0000138d")
        self.assertEqual(aia.avps[2].data, DIAMETER_MISSING_AVP)

        self.assertEqual(aia.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(aia.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(aia.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(aia.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(aia.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[6].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(aia.avps[6].dump().hex(), "000001190000003a5265717565737465642d45555452414e2d41757468656e7469636174696f6e2d496e666f20415650206e6f7420666f756e640000")
        self.assertEqual(aia.avps[6].data, b"Requested-EUTRAN-Authentication-Info AVP not found")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("air:num_answers:missing_avp"), b'1')
        cdb.decr("air:num_answers:missing_avp")

        self.assertEqual(cdb.get("air:num_requests"), b'1')
        cdb.decr("air:num_requests")

    def test__air_route__5__diameter_missing_number_of_requested_vectors_avp(self):
        #: Create Authentication-Information-Request with missing Number-Of-Requested-Vectors AVP
        request = Air.missing_number_of_requested_vectors_avp()
        aia = self.air(request)

        #: Diameter Header
        self.assertEqual(aia.header.version, DIAMETER_VERSION)
        self.assertEqual(aia.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(aia.header.command_code, AUTHENTICATION_INFORMATION_MESSAGE)
        self.assertEqual(aia.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(aia.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(aia.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(aia.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(aia.avps[2].dump().hex(), "0000010c4000000c0000138d")
        self.assertEqual(aia.avps[2].data, DIAMETER_MISSING_AVP)

        self.assertEqual(aia.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(aia.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(aia.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(aia.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(aia.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[6].code, FAILED_AVP_AVP_CODE)
        self.assertEqual(aia.avps[6].dump().hex(), "000001174000002400000580c000001c000028af00000584c0000010000028af00000001")
        self.assertEqual(aia.avps[6].requested_eutran_authentication_info_avp, request.requested_eutran_authentication_info_avp)

        self.assertEqual(aia.avps[7].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(aia.avps[7].dump().hex(), "00000119000000314e756d6265722d4f662d5265717565737465642d566563746f727320415650206e6f7420666f756e64000000")
        self.assertEqual(aia.avps[7].data, b"Number-Of-Requested-Vectors AVP not found")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("air:num_answers:missing_avp"), b'1')
        cdb.decr("air:num_answers:missing_avp")

        self.assertEqual(cdb.get("air:num_requests"), b'1')
        cdb.decr("air:num_requests")

    def test__air_route__6__diameter_success__with_immediate_response_preferred_avp(self):
        #: Create a regular Authentication-Information-Request with Immediate-Response-Preferred AVP
        aia = self.air(request=Air.with_immediate_response_preferred_avp())

        #: Diameter Header
        self.assertEqual(aia.header.version, DIAMETER_VERSION)
        self.assertEqual(aia.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(aia.header.command_code, AUTHENTICATION_INFORMATION_MESSAGE)
        self.assertEqual(aia.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(aia.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(aia.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(aia.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(aia.avps[2].dump().hex(), "0000010c4000000c000007d1")
        self.assertEqual(aia.avps[2].data, DIAMETER_SUCCESS)

        self.assertEqual(aia.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(aia.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(aia.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(aia.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(aia.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[6].code, AUTHENTICATION_INFO_AVP_CODE)
        self.assertEqual(len(aia.avps[6].avps), 1)

        self.assertEqual(aia.avps[6].e_utran_vector_avp.code, E_UTRAN_VECTOR_AVP_CODE)

        with self.assertRaises(AttributeError) as cm:
            data = aia.avps[6].e_utran_vector_avp.item_number_avp.data

        self.assertEqual(cm.exception.args[0], "'EUtranVectorAVP' object has no attribute 'item_number_avp'")

        self.assertEqual(aia.avps[6].e_utran_vector_avp.rand_avp.code, RAND_AVP_CODE)
        self.assertEqual(aia.avps[6].e_utran_vector_avp.xres_avp.code, XRES_AVP_CODE)
        self.assertEqual(aia.avps[6].e_utran_vector_avp.autn_avp.code, AUTN_AVP_CODE)
        self.assertEqual(aia.avps[6].e_utran_vector_avp.kasme_avp.code, KASME_AVP_CODE)

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("air:num_answers:success"), b'1')
        cdb.decr("air:num_answers:success")

        self.assertEqual(cdb.get("air:num_requests"), b'1')
        cdb.decr("air:num_requests")

    def test__air_route__7__diameter_success__without_immediate_response_preferred_avp__number_of_requested_vectors_2(self):
        #: Create a regular Authentication-Information-Request without Immediate-Response-Preferred AVP
        aia = self.air(request=Air.without_immediate_response_preferred_avp())

        #: Diameter Header
        self.assertEqual(aia.header.version, DIAMETER_VERSION)
        self.assertEqual(aia.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(aia.header.command_code, AUTHENTICATION_INFORMATION_MESSAGE)
        self.assertEqual(aia.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(aia.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(aia.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(aia.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(aia.avps[2].dump().hex(), "0000010c4000000c000007d1")
        self.assertEqual(aia.avps[2].data, DIAMETER_SUCCESS)

        self.assertEqual(aia.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(aia.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(aia.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(aia.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(aia.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[6].code, AUTHENTICATION_INFO_AVP_CODE)
        self.assertEqual(len(aia.avps[6].avps), 2)

        self.assertEqual(aia.avps[6].avps[0].code, E_UTRAN_VECTOR_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[0].item_number_avp.code, ITEM_NUMBER_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[0].item_number_avp.data, bytes.fromhex("00000001"))
        self.assertEqual(aia.avps[6].avps[0].rand_avp.code, RAND_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[0].xres_avp.code, XRES_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[0].autn_avp.code, AUTN_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[0].kasme_avp.code, KASME_AVP_CODE)

        self.assertEqual(aia.avps[6].avps[1].code, E_UTRAN_VECTOR_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[1].item_number_avp.code, ITEM_NUMBER_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[1].item_number_avp.data, bytes.fromhex("00000002"))
        self.assertEqual(aia.avps[6].avps[1].rand_avp.code, RAND_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[1].xres_avp.code, XRES_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[1].autn_avp.code, AUTN_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[1].kasme_avp.code, KASME_AVP_CODE)

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("air:num_answers:success"), b'1')
        cdb.decr("air:num_answers:success")

        self.assertEqual(cdb.get("air:num_requests"), b'1')
        cdb.decr("air:num_requests")

    def test__air_route__8__diameter_success__without_immediate_response_preferred_avp__number_of_requested_vectors_3(self):
        #: Create a regular Authentication-Information-Request without Immediate-Response-Preferred AVP
        aia = self.air(request=Air.without_immediate_response_preferred_avp(3))

        #: Diameter Header
        self.assertEqual(aia.header.version, DIAMETER_VERSION)
        self.assertEqual(aia.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(aia.header.command_code, AUTHENTICATION_INFORMATION_MESSAGE)
        self.assertEqual(aia.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(aia.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(aia.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(aia.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(aia.avps[2].dump().hex(), "0000010c4000000c000007d1")
        self.assertEqual(aia.avps[2].data, DIAMETER_SUCCESS)

        self.assertEqual(aia.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(aia.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(aia.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(aia.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(aia.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[6].code, AUTHENTICATION_INFO_AVP_CODE)
        self.assertEqual(len(aia.avps[6].avps), 3)

        self.assertEqual(aia.avps[6].avps[0].code, E_UTRAN_VECTOR_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[0].item_number_avp.code, ITEM_NUMBER_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[0].item_number_avp.data, bytes.fromhex("00000001"))
        self.assertEqual(aia.avps[6].avps[0].rand_avp.code, RAND_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[0].xres_avp.code, XRES_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[0].autn_avp.code, AUTN_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[0].kasme_avp.code, KASME_AVP_CODE)

        self.assertEqual(aia.avps[6].avps[1].code, E_UTRAN_VECTOR_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[1].item_number_avp.code, ITEM_NUMBER_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[1].item_number_avp.data, bytes.fromhex("00000002"))
        self.assertEqual(aia.avps[6].avps[1].rand_avp.code, RAND_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[1].xres_avp.code, XRES_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[1].autn_avp.code, AUTN_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[1].kasme_avp.code, KASME_AVP_CODE)

        self.assertEqual(aia.avps[6].avps[2].code, E_UTRAN_VECTOR_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[2].item_number_avp.code, ITEM_NUMBER_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[2].item_number_avp.data, bytes.fromhex("00000003"))
        self.assertEqual(aia.avps[6].avps[2].rand_avp.code, RAND_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[2].xres_avp.code, XRES_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[2].autn_avp.code, AUTN_AVP_CODE)
        self.assertEqual(aia.avps[6].avps[2].kasme_avp.code, KASME_AVP_CODE)

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("air:num_answers:success"), b'1')
        cdb.decr("air:num_answers:success")

        self.assertEqual(cdb.get("air:num_requests"), b'1')
        cdb.decr("air:num_requests")

    def test__air_route__9__diameter_authentication_data_unavailable__too_much_immediate_response_preferred(self):
        #: Create a regular Authentication-Information-Request with too much Immediate-Response-Preferred AVPs
        request = Air.too_much_immediate_response_preferred()
        aia = self.air(request)

        #: Diameter Header
        self.assertEqual(aia.header.version, DIAMETER_VERSION)
        self.assertEqual(aia.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(aia.header.command_code, AUTHENTICATION_INFORMATION_MESSAGE)
        self.assertEqual(aia.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(aia.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(aia.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(aia.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(aia.avps[2].dump().hex(), "0000010c4000000c00001055")
        self.assertEqual(aia.avps[2].data, DIAMETER_AUTHENTICATION_DATA_UNAVAILABLE)

        self.assertEqual(aia.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(aia.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(aia.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(aia.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(aia.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[6].code, FAILED_AVP_AVP_CODE)
        self.assertEqual(aia.avps[6].dump().hex(), "000001174000003400000580c000002c000028af00000582c0000010000028af0000000200000584c0000010000028af00000005")
        self.assertEqual(aia.avps[6].requested_eutran_authentication_info_avp, request.requested_eutran_authentication_info_avp)

        self.assertEqual(aia.avps[7].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(aia.avps[7].dump().hex(), "0000011900000046546f6f206d75636820766563746f72732072657175657374656420696e20496d6d6564696174652d526573706f6e73652d507265666572726564204156500000")
        self.assertEqual(aia.avps[7].data, b"Too much vectors requested in Immediate-Response-Preferred AVP")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("air:num_answers:authentication_data_unavailable"), b'1')
        cdb.decr("air:num_answers:authentication_data_unavailable")

        self.assertEqual(cdb.get("air:num_requests"), b'1')
        cdb.decr("air:num_requests")

    def test__air_route__10__diameter_authentication_data_unavailable__too_much_number_of_requested_vectors(self):
        #: Create a regular Authentication-Information-Request with too much Immediate-Response-Preferred AVPs
        request = Air.too_much_number_of_requested_vectors()
        aia = self.air(request)

        #: Diameter Header
        self.assertEqual(aia.header.version, DIAMETER_VERSION)
        self.assertEqual(aia.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(aia.header.command_code, AUTHENTICATION_INFORMATION_MESSAGE)
        self.assertEqual(aia.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(aia.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(aia.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(aia.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(aia.avps[2].dump().hex(), "0000010c4000000c00001055")
        self.assertEqual(aia.avps[2].data, DIAMETER_AUTHENTICATION_DATA_UNAVAILABLE)

        self.assertEqual(aia.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(aia.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(aia.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(aia.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(aia.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(aia.avps[6].code, FAILED_AVP_AVP_CODE)
        self.assertEqual(aia.avps[6].dump().hex(), "000001174000002400000580c000001c000028af00000582c0000010000028af00000005")
        self.assertEqual(aia.avps[6].requested_eutran_authentication_info_avp, request.requested_eutran_authentication_info_avp)

        self.assertEqual(aia.avps[7].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(aia.avps[7].dump().hex(), "0000011900000045546f6f206d75636820766563746f72732072657175657374656420696e204e756d6265722d4f662d5265717565737465642d566563746f727320415650000000")
        self.assertEqual(aia.avps[7].data, b"Too much vectors requested in Number-Of-Requested-Vectors AVP")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("air:num_answers:authentication_data_unavailable"), b'1')
        cdb.decr("air:num_answers:authentication_data_unavailable")

        self.assertEqual(cdb.get("air:num_requests"), b'1')
        cdb.decr("air:num_requests")


# @unittest.skip
class TestNorRoute(unittest.TestCase):
    def setUp(self):
        #: Get route functions
        self.nor = app.get_route("nor")
        self.ulr = app.get_route("ulr")

        #: Setup variables to APN creation
        self.base_url_apn = "http://localhost:5001/apns"

        content = {
            "apn_id": 1,
            "apn_name": "internet",
            "pdn_type": "IPv4v6",
            "qci": 9,
            "priority_level": 8,
            "max_req_bw_ul": 999999999,
            "max_req_bw_dl": 999999999
        }

        #: Create APN
        r = requests.post(
            self.base_url_apn, 
            data=json.dumps(content), 
            headers={"Content-Type": "application/json"}
        )

        #: Setup variables to subscriber creation
        self.base_url_subscriber = "http://localhost:5001/subscribers"

        content = {
            "identities": {
                "imsi": "999000000000001",
                "msisdn": "5521000000001"
            },
            "auth": {
                "key": "465b5ce8b199b49faa5f0a2ee238a6bc",
                "opc": "013d7d16d7ad4fefb61bd95b765c8ceb",
                "amf": "b9b9",
                "sqn": "ff9bb4d0b607"
            },
            "subscription": {
                "schar": 8,
                "stn_sr": "5500599999999",
                "odb": "ODB-VPLMN-APN",
                "roaming_allowed": False,
                "max_req_bw_ul": 100000,
                "max_req_bw_dl": 100000,
                "default_apn": 1,
                "apns": [
                    1
                ]
            }
        }

        #: Create Subscriber
        r = requests.post(
            self.base_url_subscriber, 
            data=json.dumps(content), 
            headers={"Content-Type": "application/json"}
        )

    def tearDown(self):
        #: Delete Subscriber
        r = requests.delete(f"{self.base_url_subscriber}/imsi/999000000000001")

        #: Delete APN
        r = requests.delete(f"{self.base_url_apn}/1")

    def test__nor_route__0__diameter_missing_user_name_avp(self):
        #: Create Notify-Request with missing User-Name AVP
        noa = self.nor(request=Nor.missing_user_name_avp())

        #: Diameter Header
        self.assertEqual(noa.header.version, DIAMETER_VERSION)
        self.assertEqual(noa.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(noa.header.command_code, NOTIFY_MESSAGE)
        self.assertEqual(noa.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(noa.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(noa.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(noa.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(noa.avps[2].dump().hex(), "0000010c4000000c0000138d")
        self.assertEqual(noa.avps[2].data, DIAMETER_MISSING_AVP)

        self.assertEqual(noa.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(noa.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(noa.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(noa.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(noa.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.avps[6].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(noa.avps[6].dump().hex(), "000001190000001f557365722d4e616d6520415650206e6f7420666f756e6400")
        self.assertEqual(noa.avps[6].data, b"User-Name AVP not found")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("nor:num_answers:missing_avp"), b'1')
        cdb.decr("nor:num_answers:missing_avp")

        self.assertEqual(cdb.get("nor:num_requests"), b'1')
        cdb.decr("nor:num_requests")

    def test__nor_route__1__diameter_invalid_user_name_avp_value(self):
        #: Create Notify-Request with missing User-Name AVP
        request = Nor.invalid_user_name_avp()
        noa = self.nor(request)

        #: Diameter Header
        self.assertEqual(noa.header.version, DIAMETER_VERSION)
        self.assertEqual(noa.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(noa.header.command_code, NOTIFY_MESSAGE)
        self.assertEqual(noa.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(noa.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(noa.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(noa.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(noa.avps[2].dump().hex(), "0000010c4000000c0000138c")
        self.assertEqual(noa.avps[2].data, DIAMETER_INVALID_AVP_VALUE)

        self.assertEqual(noa.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(noa.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(noa.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(noa.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(noa.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.avps[6].code, FAILED_AVP_AVP_CODE)
        self.assertEqual(noa.avps[6].dump().hex(), "0000011740000020000000014000001539393930303030303030303030000000")
        self.assertEqual(noa.avps[6].user_name_avp, request.user_name_avp)

        self.assertEqual(noa.avps[7].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(noa.avps[7].dump().hex(), "0000011900000027557365722d4e616d65204156502068617320696e76616c69642076616c756500")
        self.assertEqual(noa.avps[7].data, b"User-Name AVP has invalid value")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("nor:num_answers:invalid_avp_value"), b'1')
        cdb.decr("nor:num_answers:invalid_avp_value")

        self.assertEqual(cdb.get("nor:num_requests"), b'1')
        cdb.decr("nor:num_requests")

    def test__nor_route__2__diameter_error_user_unknown(self):
        #: Create Notify-Request with unknown user
        noa = self.nor(request=Nor.error_user_unknown())

        #: Diameter Header
        self.assertEqual(noa.header.version, DIAMETER_VERSION)
        self.assertEqual(noa.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(noa.header.command_code, NOTIFY_MESSAGE)
        self.assertEqual(noa.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(noa.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(noa.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(noa.avps[2].code, EXPERIMENTAL_RESULT_AVP_CODE)
        self.assertEqual(noa.avps[2].dump().hex(), "00000129000000200000012a4000000c000013890000010a4000000c000028af")
        self.assertEqual(noa.avps[2].experimental_result_code_avp.data, DIAMETER_ERROR_USER_UNKNOWN)

        self.assertEqual(noa.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(noa.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(noa.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(noa.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(noa.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("nor:num_answers:user_unknown"), b'1')
        cdb.decr("nor:num_answers:user_unknown")

        self.assertEqual(cdb.get("nor:num_requests"), b'1')
        cdb.decr("nor:num_requests")

    def test__nor_route__3__diameter_error_unknown_serving_node(self):
        #: It assumes that before sending a NOR message with new MME hostname
        #: a previous ULR procedure has been taken place. This is important
        #: since the last step of NOR route function is checking if there is
        #: a new MME hostname in NOR (differently from ULR's previous one)
        ula = self.ulr(request=Ulr.regular())

        #: Create Notify-Request with unknown serving node (MME)
        noa = self.nor(request=Nor.error_unknown_serving_node())

        #: Diameter Header
        self.assertEqual(noa.header.version, DIAMETER_VERSION)
        self.assertEqual(noa.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(noa.header.command_code, NOTIFY_MESSAGE)
        self.assertEqual(noa.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(noa.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(noa.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(noa.avps[2].code, EXPERIMENTAL_RESULT_AVP_CODE)
        self.assertEqual(noa.avps[2].dump().hex(), "00000129000000200000012a4000000c0000152f0000010a4000000c000028af")
        self.assertEqual(noa.avps[2].experimental_result_code_avp.data, DIAMETER_ERROR_UNKOWN_SERVING_NODE)

        self.assertEqual(noa.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(noa.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(noa.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(noa.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(noa.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("nor:num_answers:unknown_serving_node"), b'1')
        cdb.decr("nor:num_answers:unknown_serving_node")

        self.assertEqual(cdb.get("nor:num_requests"), b'1')
        cdb.decr("nor:num_requests")

        self.assertEqual(cdb.get("ulr:num_answers:success"), b'1')
        cdb.decr("ulr:num_answers:success")

        self.assertEqual(cdb.get("ulr:num_requests"), b'1')
        cdb.decr("ulr:num_requests")
    
    def test__nor_route__4__diameter_success(self):
        #: Create a regular Notify-Request
        noa = self.nor(request=Nor.regular())

        #: Diameter Header
        self.assertEqual(noa.header.version, DIAMETER_VERSION)
        self.assertEqual(noa.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(noa.header.command_code, NOTIFY_MESSAGE)
        self.assertEqual(noa.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(noa.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(noa.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(noa.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(noa.avps[2].dump().hex(), "0000010c4000000c000007d1")
        self.assertEqual(noa.avps[2].data, DIAMETER_SUCCESS)

        self.assertEqual(noa.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(noa.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(noa.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(noa.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(noa.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("nor:num_answers:success"), b'1')
        cdb.decr("nor:num_answers:success")

        self.assertEqual(cdb.get("nor:num_requests"), b'1')
        cdb.decr("nor:num_requests")

    def test__nor_route__5__diameter_missing_mip6_agent_info_avp(self):
        #: Create Notify-Request with missing Mip6-Agent-Info AVP
        noa = self.nor(request=Nor.missing_mip6_agent_info_avp())

        #: Diameter Header
        self.assertEqual(noa.header.version, DIAMETER_VERSION)
        self.assertEqual(noa.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(noa.header.command_code, NOTIFY_MESSAGE)
        self.assertEqual(noa.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(noa.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(noa.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(noa.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(noa.avps[2].dump().hex(), "0000010c4000000c0000138d")
        self.assertEqual(noa.avps[2].data, DIAMETER_MISSING_AVP)

        self.assertEqual(noa.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(noa.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(noa.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(noa.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(noa.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.avps[6].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(noa.avps[6].dump().hex(), "00000119000000254d4950362d4167656e742d496e666f20415650206e6f7420666f756e64000000")
        self.assertEqual(noa.avps[6].data, b"MIP6-Agent-Info AVP not found")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("nor:num_answers:missing_avp"), b'1')
        cdb.decr("nor:num_answers:missing_avp")

        self.assertEqual(cdb.get("nor:num_requests"), b'1')
        cdb.decr("nor:num_requests")

    def test__nor_route__6__diameter_missing_mip6_agent_info_avp__mip_home_agent_host(self):
        #: Create Notify-Request with missing Mip-Home-Agent-Host AVP in Mip6-Agent-Info AVP
        request = Nor.missing_mip_home_agent_host_avp()
        noa = self.nor(request)

        #: Diameter Header
        self.assertEqual(noa.header.version, DIAMETER_VERSION)
        self.assertEqual(noa.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(noa.header.command_code, NOTIFY_MESSAGE)
        self.assertEqual(noa.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(noa.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(noa.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(noa.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(noa.avps[2].dump().hex(), "0000010c4000000c0000138d")
        self.assertEqual(noa.avps[2].data, DIAMETER_MISSING_AVP)

        self.assertEqual(noa.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(noa.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(noa.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(noa.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(noa.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.avps[6].code, FAILED_AVP_AVP_CODE)
        self.assertEqual(noa.avps[6].dump().hex(), "0000011740000010000001e640000008")
        self.assertEqual(noa.avps[6].data.hex(), "000001e640000008")
        self.assertEqual(noa.avps[6].mip6_agent_info_avp, request.mip6_agent_info_avp)

        self.assertEqual(noa.avps[7].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(noa.avps[7].dump().hex(), "00000119000000294d49502d486f6d652d4167656e742d486f737420415650206e6f7420666f756e64000000")
        self.assertEqual(noa.avps[7].data, b"MIP-Home-Agent-Host AVP not found")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("nor:num_answers:missing_avp"), b'1')
        cdb.decr("nor:num_answers:missing_avp")

        self.assertEqual(cdb.get("nor:num_requests"), b'1')
        cdb.decr("nor:num_requests")

    def test__nor_route__7__diameter_missing_mip6_agent_info_avp__destination_host(self):
        #: Create Notify-Request with missing Destination-Host AVP in Mip-Home-Agent-Host AVP
        request = Nor.missing_destination_host_in_mip6_agent_info_avp()
        noa = self.nor(request)

        #: Diameter Header
        self.assertEqual(noa.header.version, DIAMETER_VERSION)
        self.assertEqual(noa.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(noa.header.command_code, NOTIFY_MESSAGE)
        self.assertEqual(noa.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(noa.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(noa.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(noa.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(noa.avps[2].dump().hex(), "0000010c4000000c0000138d")
        self.assertEqual(noa.avps[2].data, DIAMETER_MISSING_AVP)

        self.assertEqual(noa.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(noa.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(noa.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(noa.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(noa.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.avps[6].code, FAILED_AVP_AVP_CODE)
        self.assertEqual(noa.avps[6].dump().hex(), "0000011740000080000001e6400000780000015c400000700000011b400000296570632e6d6e635858582e6d63635959592e336770706e6574776f726b2e6f7267000000000001254000003a746f706f6e2e73357067772e6e6f64652e6570632e6d6e635858582e6d63635959592e336770706e6574776f726b2e6f72670000")
        self.assertEqual(noa.avps[6].data.hex(), "000001e6400000780000015c400000700000011b400000296570632e6d6e635858582e6d63635959592e336770706e6574776f726b2e6f7267000000000001254000003a746f706f6e2e73357067772e6e6f64652e6570632e6d6e635858582e6d63635959592e336770706e6574776f726b2e6f72670000")
        self.assertEqual(noa.avps[6].mip6_agent_info_avp, request.mip6_agent_info_avp)

        self.assertEqual(noa.avps[7].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(noa.avps[7].dump().hex(), "000001190000002644657374696e6174696f6e2d486f737420415650206e6f7420666f756e640000")
        self.assertEqual(noa.avps[7].data, b"Destination-Host AVP not found")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("nor:num_answers:missing_avp"), b'1')
        cdb.decr("nor:num_answers:missing_avp")

        self.assertEqual(cdb.get("nor:num_requests"), b'1')
        cdb.decr("nor:num_requests")

    def test__nor_route__8__diameter_missing_mip6_agent_info_avp__destination_realm(self):
        #: Create Notify-Request with missing Destination-Realm AVP in Mip-Home-Agent-Host AVP
        request = Nor.missing_destination_realm_in_mip6_agent_info_avp()
        noa = self.nor(request)

        #: Diameter Header
        self.assertEqual(noa.header.version, DIAMETER_VERSION)
        self.assertEqual(noa.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(noa.header.command_code, NOTIFY_MESSAGE)
        self.assertEqual(noa.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(noa.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(noa.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(noa.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(noa.avps[2].dump().hex(), "0000010c4000000c0000138d")
        self.assertEqual(noa.avps[2].data, DIAMETER_MISSING_AVP)

        self.assertEqual(noa.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(noa.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(noa.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(noa.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(noa.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(noa.avps[6].code, FAILED_AVP_AVP_CODE)
        self.assertEqual(noa.avps[6].dump().hex(), "0000011740000080000001e6400000780000015c400000700000011b400000296570632e6d6e635858582e6d63635959592e336770706e6574776f726b2e6f7267000000000001254000003a746f706f6e2e73357067772e6e6f64652e6570632e6d6e635858582e6d63635959592e336770706e6574776f726b2e6f72670000")
        self.assertEqual(noa.avps[6].data.hex(), "000001e6400000780000015c400000700000011b400000296570632e6d6e635858582e6d63635959592e336770706e6574776f726b2e6f7267000000000001254000003a746f706f6e2e73357067772e6e6f64652e6570632e6d6e635858582e6d63635959592e336770706e6574776f726b2e6f72670000")
        self.assertEqual(noa.avps[6].mip6_agent_info_avp, request.mip6_agent_info_avp)

        self.assertEqual(noa.avps[7].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(noa.avps[7].dump().hex(), "000001190000002744657374696e6174696f6e2d5265616c6d20415650206e6f7420666f756e6400")
        self.assertEqual(noa.avps[7].data, b"Destination-Realm AVP not found")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("nor:num_answers:missing_avp"), b'1')
        cdb.decr("nor:num_answers:missing_avp")

        self.assertEqual(cdb.get("nor:num_requests"), b'1')
        cdb.decr("nor:num_requests")


# @unittest.skip
class TestPurRoute(unittest.TestCase):
    def setUp(self):
        #: Get route functions
        self.pur = app.get_route("pur")
        self.ulr = app.get_route("ulr")

        #: Setup variables to APN creation
        self.base_url_apn = "http://localhost:5001/apns"

        content = {
            "apn_id": 1,
            "apn_name": "internet",
            "pdn_type": "IPv4v6",
            "qci": 9,
            "priority_level": 8,
            "max_req_bw_ul": 999999999,
            "max_req_bw_dl": 999999999
        }

        #: Create APN
        r = requests.post(
            self.base_url_apn, 
            data=json.dumps(content), 
            headers={"Content-Type": "application/json"}
        )

        #: Setup variables to subscriber creation
        self.base_url_subscriber = "http://localhost:5001/subscribers"

        content = {
            "identities": {
                "imsi": "999000000000001",
                "msisdn": "5521000000001"
            },
            "auth": {
                "key": "465b5ce8b199b49faa5f0a2ee238a6bc",
                "opc": "013d7d16d7ad4fefb61bd95b765c8ceb",
                "amf": "b9b9",
                "sqn": "ff9bb4d0b607"
            },
            "subscription": {
                "schar": 8,
                "stn_sr": "5500599999999",
                "odb": "ODB-VPLMN-APN",
                "roaming_allowed": False,
                "max_req_bw_ul": 100000,
                "max_req_bw_dl": 100000,
                "default_apn": 1,
                "apns": [
                    1
                ]
            }
        }

        #: Create Subscriber
        r = requests.post(
            self.base_url_subscriber, 
            data=json.dumps(content), 
            headers={"Content-Type": "application/json"}
        )

    def tearDown(self):
        #: Delete Subscriber
        r = requests.delete(f"{self.base_url_subscriber}/imsi/999000000000001")

        #: Delete APN
        r = requests.delete(f"{self.base_url_apn}/1")

    def test__pur_route__0__diameter_missing_user_name_avp(self):
        #: Create Purge-UE-Request with missing User-Name AVP
        pua = self.pur(request=Pur.missing_user_name_avp())

        #: Diameter Header
        self.assertEqual(pua.header.version, DIAMETER_VERSION)
        self.assertEqual(pua.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(pua.header.command_code, PURGE_UE_MESSAGE)
        self.assertEqual(pua.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(pua.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(pua.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(pua.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(pua.avps[2].dump().hex(), "0000010c4000000c0000138d")
        self.assertEqual(pua.avps[2].data, DIAMETER_MISSING_AVP)

        self.assertEqual(pua.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(pua.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(pua.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(pua.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(pua.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(pua.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(pua.avps[6].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(pua.avps[6].dump().hex(), "000001190000001f557365722d4e616d6520415650206e6f7420666f756e6400")
        self.assertEqual(pua.avps[6].data, b"User-Name AVP not found")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("pur:num_answers:missing_avp"), b'1')
        cdb.decr("pur:num_answers:missing_avp")

        self.assertEqual(cdb.get("pur:num_requests"), b'1')
        cdb.decr("pur:num_requests")

    def test__pur_route__1__diameter_invalid_user_name_avp_value(self):
        #: Create Purge-UE-Request with invalid User-Name AVP value (less than 15 length digits)
        request = Pur.invalid_user_name_avp()
        pua = self.pur(request)

        #: Diameter Header
        self.assertEqual(pua.header.version, DIAMETER_VERSION)
        self.assertEqual(pua.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(pua.header.command_code, PURGE_UE_MESSAGE)
        self.assertEqual(pua.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(pua.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(pua.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(pua.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(pua.avps[2].dump().hex(), "0000010c4000000c0000138c")
        self.assertEqual(pua.avps[2].data, DIAMETER_INVALID_AVP_VALUE)

        self.assertEqual(pua.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(pua.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(pua.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(pua.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(pua.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(pua.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(pua.avps[6].code, FAILED_AVP_AVP_CODE)
        self.assertEqual(pua.avps[6].dump().hex(), "0000011740000020000000014000001539393930303030303030303030000000")
        self.assertEqual(pua.avps[6].user_name_avp, request.user_name_avp)

        self.assertEqual(pua.avps[7].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(pua.avps[7].dump().hex(), "0000011900000027557365722d4e616d65204156502068617320696e76616c69642076616c756500")
        self.assertEqual(pua.avps[7].data, b"User-Name AVP has invalid value")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("pur:num_answers:invalid_avp_value"), b'1')
        cdb.decr("pur:num_answers:invalid_avp_value")

        self.assertEqual(cdb.get("pur:num_requests"), b'1')
        cdb.decr("pur:num_requests")

    def test__pur_route__3__diameter_error_user_unknown(self):
        #: Create Purge-UE-Request with unknown user
        pua = self.pur(request=Pur.error_user_unknown())

        #: Diameter Header
        self.assertEqual(pua.header.version, DIAMETER_VERSION)
        self.assertEqual(pua.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(pua.header.command_code, PURGE_UE_MESSAGE)
        self.assertEqual(pua.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(pua.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(pua.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(pua.avps[2].code, EXPERIMENTAL_RESULT_AVP_CODE)
        self.assertEqual(pua.avps[2].dump().hex(), "00000129000000200000012a4000000c000013890000010a4000000c000028af")
        self.assertEqual(pua.avps[2].experimental_result_code_avp.data, DIAMETER_ERROR_USER_UNKNOWN)

        self.assertEqual(pua.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(pua.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(pua.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(pua.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(pua.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(pua.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("pur:num_answers:user_unknown"), b'1')
        cdb.decr("pur:num_answers:user_unknown")

        self.assertEqual(cdb.get("pur:num_requests"), b'1')
        cdb.decr("pur:num_requests")

    def test__pur_route__4__diameter_success(self):
        #: Create a regular Purge-UE-Request
        pua = self.pur(request=Pur.regular())

        #: Diameter Header
        self.assertEqual(pua.header.version, DIAMETER_VERSION)
        self.assertEqual(pua.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(pua.header.command_code, PURGE_UE_MESSAGE)
        self.assertEqual(pua.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(pua.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(pua.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(pua.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(pua.avps[2].dump().hex(), "0000010c4000000c000007d1")
        self.assertEqual(pua.avps[2].data, DIAMETER_SUCCESS)

        self.assertEqual(pua.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(pua.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(pua.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(pua.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(pua.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(pua.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(pua.avps[6].code, PUA_FLAGS_AVP_CODE)
        self.assertEqual(pua.avps[6].dump().hex(), "000005a2c0000010000028af00000001")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("pur:num_answers:success"), b'1')
        cdb.decr("pur:num_answers:success")

        self.assertEqual(cdb.get("pur:num_requests"), b'1')
        cdb.decr("pur:num_requests")

    def test__pur_route__5__diameter_success_with_new_mme(self):
        #: It assumes that before sending a PUR message with new MME hostname
        #: a previous ULR procedure has been taken place. This is important
        #: since the last step of PUR route function is checking if there is
        #: a new MME hostname in PUR (differently from ULR's previous one)
        ula = self.ulr(request=Ulr.regular())

        #: Create Purge-UE-Request with unknown serving node (MME)
        pua = self.pur(request=Pur.error_unknown_serving_node())

        #: Diameter Header
        self.assertEqual(pua.header.version, DIAMETER_VERSION)
        self.assertEqual(pua.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(pua.header.command_code, PURGE_UE_MESSAGE)
        self.assertEqual(pua.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(pua.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(pua.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(pua.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(pua.avps[2].dump().hex(), "0000010c4000000c000007d1")
        self.assertEqual(pua.avps[2].data, DIAMETER_SUCCESS)

        self.assertEqual(pua.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(pua.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(pua.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(pua.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(pua.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(pua.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(pua.avps[6].code, PUA_FLAGS_AVP_CODE)
        self.assertEqual(pua.avps[6].dump().hex(), "000005a2c0000010000028af00000000")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("pur:num_answers:success"), b'1')
        cdb.decr("pur:num_answers:success")

        self.assertEqual(cdb.get("pur:num_requests"), b'1')
        cdb.decr("pur:num_requests")

        self.assertEqual(cdb.get("ulr:num_answers:success"), b'1')
        cdb.decr("ulr:num_answers:success")

        self.assertEqual(cdb.get("ulr:num_requests"), b'1')
        cdb.decr("ulr:num_requests")


# @unittest.skip
class TestUlrRoute(unittest.TestCase):
    def setUp(self):
        #: Get route function
        self.ulr = app.get_route("ulr")

        #: Setup variables to APN creation
        self.base_url_apn = "http://localhost:5001/apns"

        #: Create APN internet
        content = {
            "apn_id": 1,
            "apn_name": "internet",
            "pdn_type": "IPv4",
            "qci": 9,
            "priority_level": 8,
            "max_req_bw_ul": 999999999,
            "max_req_bw_dl": 999999999
        }

        r = requests.post(
            self.base_url_apn, 
            data=json.dumps(content), 
            headers={"Content-Type": "application/json"}
        )

        #: Create APN mms
        content = {
            "apn_id": 3,
            "apn_name": "mms",
            "pdn_type": "IPv4",
            "qci": 9,
            "priority_level": 8,
            "max_req_bw_ul": 256,
            "max_req_bw_dl": 256
        }

        r = requests.post(
            self.base_url_apn, 
            data=json.dumps(content), 
            headers={"Content-Type": "application/json"}
        )

        #: Create APN internetlte
        content = {
            "apn_id": 4,
            "apn_name": "internetlte",
            "pdn_type": "IPv4v6",
            "qci": 9,
            "priority_level": 8,
            "max_req_bw_ul": 999999999,
            "max_req_bw_dl": 999999999
        }

        r = requests.post(
            self.base_url_apn, 
            data=json.dumps(content), 
            headers={"Content-Type": "application/json"}
        )

        #: Create APN ims
        content = {
            "apn_id": 824,
            "apn_name": "ims",
            "pdn_type": "IPv4v6",
            "qci": 5,
            "priority_level": 8,
            "max_req_bw_ul": 256,
            "max_req_bw_dl": 256
        }

        r = requests.post(
            self.base_url_apn, 
            data=json.dumps(content), 
            headers={"Content-Type": "application/json"}
        )

        #: Setup variables to subscriber creation
        self.base_url_subscriber = "http://localhost:5001/subscribers"

        content = {
            "identities": {
                "imsi": "999000000000001",
                "msisdn": "5521000000001"
            },
            "auth": {
                "key": "465b5ce8b199b49faa5f0a2ee238a6bc",
                "opc": "013d7d16d7ad4fefb61bd95b765c8ceb",
                "amf": "b9b9",
                "sqn": "ff9bb4d0b607"
            },
            "subscription": {
                "schar": 8,
                "stn_sr": "5500599999999",
                "roaming_allowed": False,
                "max_req_bw_ul": 100000,
                "max_req_bw_dl": 100000,
                "default_apn": 1,
                "apns": [
                    1,
                    3,
                    4,
                    824
                ]
            }
        }

        #: Create Subscriber #1
        r = requests.post(
            self.base_url_subscriber, 
            data=json.dumps(content), 
            headers={"Content-Type": "application/json"}
        )

        #: Create Subscriber #2
        self.subscriber_with_odb_all_apn = "999000000000002"
        content["identities"]["imsi"] = self.subscriber_with_odb_all_apn
        content["identities"]["msisdn"] = "5521000000002"
        content["subscription"]["odb"] = "ODB-all-APN"

        r = requests.post(
            self.base_url_subscriber, 
            data=json.dumps(content), 
            headers={"Content-Type": "application/json"}
        )

        #: Create Subscriber #3
        self.subscriber_with_odb_hplmn_apn = "999000000000003"
        content["identities"]["imsi"] = self.subscriber_with_odb_hplmn_apn
        content["identities"]["msisdn"] = "5521000000003"
        content["subscription"]["odb"] = "ODB-HPLMN-APN"

        r = requests.post(
            self.base_url_subscriber, 
            data=json.dumps(content), 
            headers={"Content-Type": "application/json"}
        )

        #: Create Subscriber #4
        self.subscriber_with_odb_vplmn_apn = "999000000000004"
        content["identities"]["imsi"] = self.subscriber_with_odb_vplmn_apn
        content["identities"]["msisdn"] = "5521000000004"
        content["subscription"]["odb"] = "ODB-VPLMN-APN"

        r = requests.post(
            self.base_url_subscriber, 
            data=json.dumps(content), 
            headers={"Content-Type": "application/json"}
        )

    def tearDown(self):
        #: Delete Subscribers
        r = requests.delete(f"{self.base_url_subscriber}/imsi/999000000000001")
        r = requests.delete(f"{self.base_url_subscriber}/imsi/999000000000002")
        r = requests.delete(f"{self.base_url_subscriber}/imsi/999000000000003")
        r = requests.delete(f"{self.base_url_subscriber}/imsi/999000000000004")

        #: Delete APN
        r = requests.delete(f"{self.base_url_apn}/1")
        r = requests.delete(f"{self.base_url_apn}/3")
        r = requests.delete(f"{self.base_url_apn}/4")
        r = requests.delete(f"{self.base_url_apn}/824")

    def test__ulr_route__0__diameter_missing_user_name_avp(self):
        #: Create Update-Location-Request with missing User-Name AVP
        ula = self.ulr(request=Ulr.missing_user_name_avp())

        #: Diameter Header
        self.assertEqual(ula.header.version, DIAMETER_VERSION)
        self.assertEqual(ula.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(ula.header.command_code, UPDATE_LOCATION_MESSAGE)
        self.assertEqual(ula.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(ula.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(ula.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(ula.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(ula.avps[2].dump().hex(), "0000010c4000000c0000138d")
        self.assertEqual(ula.avps[2].data, DIAMETER_MISSING_AVP)

        self.assertEqual(ula.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(ula.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(ula.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(ula.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(ula.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[6].code, SUPPORTED_FEATURES_AVP_CODE)
        self.assertEqual(ula.avps[6].dump().hex(), "0000027480000038000028af0000010a4000000c000028af0000027580000010000028af000000010000027680000010000028af00000007")

        self.assertEqual(ula.avps[7].code, ULA_FLAGS_AVP_CODE)
        self.assertEqual(ula.avps[7].dump().hex(), "0000057ec0000010000028af00000001")

        self.assertEqual(ula.avps[8].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(ula.avps[8].dump().hex(), "000001190000001f557365722d4e616d6520415650206e6f7420666f756e6400")
        self.assertEqual(ula.avps[8].data, b"User-Name AVP not found")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("ulr:num_answers:missing_avp"), b'1')
        cdb.decr("ulr:num_answers:missing_avp")

        self.assertEqual(cdb.get("ulr:num_requests"), b'1')
        cdb.decr("ulr:num_requests")

    def test__ulr_route__1__diameter_invalid_user_name_avp_value(self):
        #: Create Update-Location-Request with invalid User-Name AVP value (less than 15 length digits)
        request = Ulr.invalid_user_name_avp()
        ula = self.ulr(request)

        #: Diameter Header
        self.assertEqual(ula.header.version, DIAMETER_VERSION)
        self.assertEqual(ula.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(ula.header.command_code, UPDATE_LOCATION_MESSAGE)
        self.assertEqual(ula.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(ula.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(ula.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(ula.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(ula.avps[2].dump().hex(), "0000010c4000000c0000138c")
        self.assertEqual(ula.avps[2].data, DIAMETER_INVALID_AVP_VALUE)

        self.assertEqual(ula.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(ula.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(ula.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(ula.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(ula.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[6].code, SUPPORTED_FEATURES_AVP_CODE)
        self.assertEqual(ula.avps[6].dump().hex(), "0000027480000038000028af0000010a4000000c000028af0000027580000010000028af000000010000027680000010000028af00000007")

        self.assertEqual(ula.avps[7].code, ULA_FLAGS_AVP_CODE)
        self.assertEqual(ula.avps[7].dump().hex(), "0000057ec0000010000028af00000001")

        self.assertEqual(ula.avps[8].code, FAILED_AVP_AVP_CODE)
        self.assertEqual(ula.avps[8].dump().hex(), "0000011740000020000000014000001539393930303030303030303030000000")
        self.assertEqual(ula.avps[8].user_name_avp, request.user_name_avp)

        self.assertEqual(ula.avps[9].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(ula.avps[9].dump().hex(), "0000011900000027557365722d4e616d65204156502068617320696e76616c69642076616c756500")
        self.assertEqual(ula.avps[9].data, b"User-Name AVP has invalid value")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("ulr:num_answers:invalid_avp_value"), b'1')
        cdb.decr("ulr:num_answers:invalid_avp_value")

        self.assertEqual(cdb.get("ulr:num_requests"), b'1')
        cdb.decr("ulr:num_requests")

    def test__ulr_route__2__diameter_rat_not_allowed(self):
        #: Create Update-Location-Request with RAT not allowed (WLAN)
        ula = self.ulr(request=Ulr.rat_not_allowed())

        #: Diameter Header
        self.assertEqual(ula.header.version, DIAMETER_VERSION)
        self.assertEqual(ula.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(ula.header.command_code, UPDATE_LOCATION_MESSAGE)
        self.assertEqual(ula.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(ula.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(ula.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(ula.avps[2].code, EXPERIMENTAL_RESULT_AVP_CODE)
        self.assertEqual(ula.avps[2].dump().hex(), "00000129000000200000012a4000000c0000152d0000010a4000000c000028af")
        self.assertEqual(ula.avps[2].experimental_result_code_avp.data, DIAMETER_ERROR_RAT_NOT_ALLOWED)

        self.assertEqual(ula.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(ula.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(ula.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(ula.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(ula.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[6].code, SUPPORTED_FEATURES_AVP_CODE)
        self.assertEqual(ula.avps[6].dump().hex(), "0000027480000038000028af0000010a4000000c000028af0000027580000010000028af000000010000027680000010000028af00000007")

        self.assertEqual(ula.avps[7].code, ULA_FLAGS_AVP_CODE)
        self.assertEqual(ula.avps[7].dump().hex(), "0000057ec0000010000028af00000001")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("ulr:num_answers:rat_not_allowed"), b'1')
        cdb.decr("ulr:num_answers:rat_not_allowed")

        self.assertEqual(cdb.get("ulr:num_requests"), b'1')
        cdb.decr("ulr:num_requests")

    def test__ulr_route__3__diameter_error_user_unknown(self):
        #: Create Update-Location-Request with unknown user
        ula = self.ulr(request=Ulr.error_user_unknown())

        #: Diameter Header
        self.assertEqual(ula.header.version, DIAMETER_VERSION)
        self.assertEqual(ula.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(ula.header.command_code, UPDATE_LOCATION_MESSAGE)
        self.assertEqual(ula.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(ula.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(ula.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(ula.avps[2].code, EXPERIMENTAL_RESULT_AVP_CODE)
        self.assertEqual(ula.avps[2].dump().hex(), "00000129000000200000012a4000000c000013890000010a4000000c000028af")
        self.assertEqual(ula.avps[2].experimental_result_code_avp.data, DIAMETER_ERROR_USER_UNKNOWN)

        self.assertEqual(ula.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(ula.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(ula.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(ula.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(ula.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[6].code, SUPPORTED_FEATURES_AVP_CODE)
        self.assertEqual(ula.avps[6].dump().hex(), "0000027480000038000028af0000010a4000000c000028af0000027580000010000028af000000010000027680000010000028af00000007")

        self.assertEqual(ula.avps[7].code, ULA_FLAGS_AVP_CODE)
        self.assertEqual(ula.avps[7].dump().hex(), "0000057ec0000010000028af00000001")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("ulr:num_answers:user_unknown"), b'1')
        cdb.decr("ulr:num_answers:user_unknown")

        self.assertEqual(cdb.get("ulr:num_requests"), b'1')
        cdb.decr("ulr:num_requests")

    def test__ulr_route__4__diameter_success(self):
        app.testing_answer = CLA(result_code=DIAMETER_SUCCESS)

        #: Create a regular Update-Location-Request
        ula = self.ulr(request=Ulr.regular())

        #: Diameter Header
        self.assertEqual(ula.header.version, DIAMETER_VERSION)
        self.assertEqual(ula.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(ula.header.command_code, UPDATE_LOCATION_MESSAGE)
        self.assertEqual(ula.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(ula.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(ula.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(ula.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(ula.avps[2].dump().hex(), "0000010c4000000c000007d1")
        self.assertEqual(ula.avps[2].data, DIAMETER_SUCCESS)

        self.assertEqual(ula.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(ula.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(ula.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(ula.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(ula.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[6].code, SUPPORTED_FEATURES_AVP_CODE)
        self.assertEqual(ula.avps[6].dump().hex(), "0000027480000038000028af0000010a4000000c000028af0000027580000010000028af000000010000027680000010000028af00000007")

        self.assertEqual(ula.avps[7].code, ULA_FLAGS_AVP_CODE)
        self.assertEqual(ula.avps[7].dump().hex(), "0000057ec0000010000028af00000001")

        self.maxDiff = None

        self.assertEqual(ula.avps[8].code, SUBSCRIPTION_DATA_AVP_CODE)
        self.assertEqual(ula.avps[8].dump().hex(), "00000578c0000368000028af000002bdc0000013000028af551200000000f10000000599c0000013000028af550095999999f90000000590c0000010000028af000000000000000d80000010000028af303830300000059bc000002c000028af00000204c0000010000028af000186a000000203c0000010000028af000186a000000595c00002e8000028af0000058f80000010000028af0000000100000594c0000010000028af0000000000000596c00000b0000028af0000058f80000010000028af00000001000001ed40000010696e7465726e6574000005b080000010000028af0000000000000597c0000038000028af0000040480000010000028af000000090000040a8000001c000028af0000041680000010000028af000000080000059bc000002c000028af00000203c0000010000028af3b9ac9ff00000204c0000010000028af3b9ac9ff00000598c0000010000028af0000000000000596c00000ac000028af0000058f80000010000028af00000003000001ed4000000b6d6d7300000005b080000010000028af0000000000000597c0000038000028af0000040480000010000028af000000090000040a8000001c000028af0000041680000010000028af000000080000059bc000002c000028af00000203c0000010000028af0000010000000204c0000010000028af0000010000000598c0000010000028af0000000000000596c00000b4000028af0000058f80000010000028af00000004000001ed40000013696e7465726e65746c746500000005b080000010000028af0000000200000597c0000038000028af0000040480000010000028af000000090000040a8000001c000028af0000041680000010000028af000000080000059bc000002c000028af00000203c0000010000028af3b9ac9ff00000204c0000010000028af3b9ac9ff00000598c0000010000028af0000000000000596c00000ac000028af0000058f80000010000028af00000338000001ed4000000b696d7300000005b080000010000028af0000000200000597c0000038000028af0000040480000010000028af000000050000040a8000001c000028af0000041680000010000028af000000080000059bc000002c000028af00000203c0000010000028af0000010000000204c0000010000028af0000010000000598c0000010000028af00000000")

        self.assertEqual(ula.avps[8][0].code, MSISDN_AVP_CODE)
        self.assertEqual(ula.avps[8][0].data, bytes.fromhex("551200000000f1"))

        self.assertEqual(ula.avps[8][1].code, STN_SR_AVP_CODE)
        self.assertEqual(ula.avps[8][1].data, bytes.fromhex("550095999999f9"))

        self.assertEqual(ula.avps[8][2].code, SUBSCRIBER_STATUS_AVP_CODE)
        self.assertEqual(ula.avps[8][2].data, SUBSCRIBER_STATUS_SERVICE_GRANTED)

        self.assertEqual(ula.avps[8][3].code, X_3GPP_CHARGING_CHARACTERISTICS_AVP_CODE)
        self.assertEqual(ula.avps[8][3].data, bytes.fromhex("30383030"))

        self.assertEqual(ula.avps[8][4].code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][4].data, bytes.fromhex("00000204c0000010000028af000186a000000203c0000010000028af000186a0"))
        self.assertEqual(ula.avps[8][4].max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][4].max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(100000))
        self.assertEqual(ula.avps[8][4].max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][4].max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(100000))

        self.assertEqual(ula.avps[8][5].code, APN_CONFIGURATION_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][5].context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][5].context_identifier_avp.data, convert_to_4_bytes(1))
        self.assertEqual(ula.avps[8][5].all_apn_configurations_included_indicator_avp.code, ALL_APN_CONFIGURATIONS_INCLUDED_INDICATOR_AVP_CODE)
        self.assertEqual(ula.avps[8][5].all_apn_configurations_included_indicator_avp.data, ALL_APN_CONFIGURATIONS_INCLUDED)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.context_identifier_avp.data, convert_to_4_bytes(1))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.service_selection_avp.data, b"internet")
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)

        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.context_identifier_avp.data, convert_to_4_bytes(3))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.service_selection_avp.data, b"mms")
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__1.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)

        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.context_identifier_avp.data, convert_to_4_bytes(4))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.service_selection_avp.data, b"internetlte")
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.pdn_type_avp.data, PDN_TYPE_IPV4V6)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__2.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)

        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.context_identifier_avp.data, convert_to_4_bytes(824))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.service_selection_avp.data, b"ims")
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.pdn_type_avp.data, PDN_TYPE_IPV4V6)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(5))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(ula.avps[8][5].apn_configuration_avp__3.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("ulr:num_answers:success"), b'1')
        cdb.decr("ulr:num_answers:success")

        self.assertEqual(cdb.get("ulr:num_requests"), b'1')
        cdb.decr("ulr:num_requests")

    def test__ulr_route__5__diameter_missing_visited_plmn_id_avp(self):
        #: Create Update-Location-Request with missing Visited-PLMN-Id AVP
        request = Ulr.missing_visited_plmn_id_avp()
        ula = self.ulr(request)

        #: Diameter Header
        self.assertEqual(ula.header.version, DIAMETER_VERSION)
        self.assertEqual(ula.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(ula.header.command_code, UPDATE_LOCATION_MESSAGE)
        self.assertEqual(ula.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(ula.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(ula.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(ula.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(ula.avps[2].dump().hex(), "0000010c4000000c0000138d")
        self.assertEqual(ula.avps[2].data, DIAMETER_MISSING_AVP)

        self.assertEqual(ula.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(ula.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(ula.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(ula.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(ula.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[6].code, SUPPORTED_FEATURES_AVP_CODE)
        self.assertEqual(ula.avps[6].dump().hex(), "0000027480000038000028af0000010a4000000c000028af0000027580000010000028af000000010000027680000010000028af00000007")

        self.assertEqual(ula.avps[7].code, ULA_FLAGS_AVP_CODE)
        self.assertEqual(ula.avps[7].dump().hex(), "0000057ec0000010000028af00000001")

        self.assertEqual(ula.avps[8].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(ula.avps[8].dump().hex(), "0000011900000025566973697465642d504c4d4e2d496420415650206e6f7420666f756e64000000")
        self.assertEqual(ula.avps[8].data, b"Visited-PLMN-Id AVP not found")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("ulr:num_answers:missing_avp"), b'1')
        cdb.decr("ulr:num_answers:missing_avp")

        self.assertEqual(cdb.get("ulr:num_requests"), b'1')
        cdb.decr("ulr:num_requests")

    def test__ulr_route__6__diameter_success__with_cancel_location_request(self):
        app.testing_answer = CLA(result_code=DIAMETER_SUCCESS)

        #: 1st ULR
        ula = self.ulr(request=Ulr.regular())

        #: 2nd ULR with different Origin-Host AVP value
        ula = self.ulr(request=Ulr.regular(origin_host="localhost2.domain"))

        #: Diameter Header
        self.assertEqual(ula.header.version, DIAMETER_VERSION)
        self.assertEqual(ula.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(ula.header.command_code, UPDATE_LOCATION_MESSAGE)
        self.assertEqual(ula.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(ula.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(ula.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(ula.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(ula.avps[2].dump().hex(), "0000010c4000000c000007d1")
        self.assertEqual(ula.avps[2].data, DIAMETER_SUCCESS)

        self.assertEqual(ula.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(ula.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(ula.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(ula.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(ula.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[6].code, SUPPORTED_FEATURES_AVP_CODE)
        self.assertEqual(ula.avps[6].dump().hex(), "0000027480000038000028af0000010a4000000c000028af0000027580000010000028af000000010000027680000010000028af00000007")

        self.assertEqual(ula.avps[7].code, ULA_FLAGS_AVP_CODE)
        self.assertEqual(ula.avps[7].dump().hex(), "0000057ec0000010000028af00000001")

        #: 3rd ULR with same Origin-Host AVP value observed in the 1st ULR
        ula = self.ulr(request=Ulr.regular())

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("ulr:num_answers:success"), b'3')
        cdb.decr("ulr:num_answers:success", 3)

        self.assertEqual(cdb.get("ulr:num_requests"), b'3')
        cdb.decr("ulr:num_requests", 3)

    def test__ulr_route__7__diameter_error_roaming_not_allowed__odb_all_apn(self):
        #: Create Update-Location-Request with Roamning not allowed due to subscriber provisioned with ODB-all-APN
        ula = self.ulr(request=Ulr.roaming_not_allowed(self.subscriber_with_odb_all_apn))

        #: Diameter Header
        self.assertEqual(ula.header.version, DIAMETER_VERSION)
        self.assertEqual(ula.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(ula.header.command_code, UPDATE_LOCATION_MESSAGE)
        self.assertEqual(ula.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(ula.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(ula.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(ula.avps[2].code, EXPERIMENTAL_RESULT_AVP_CODE)
        self.assertEqual(ula.avps[2].dump().hex(), "00000129000000200000012a4000000c0000138c0000010a4000000c000028af")
        self.assertEqual(ula.avps[2].experimental_result_code_avp.data, DIAMETER_ERROR_ROAMING_NOT_ALLOWED)

        self.assertEqual(ula.avps[3].code, ERROR_DIAGNOSTIC_AVP_CODE)
        self.assertEqual(ula.avps[3].dump().hex(), "0000064e80000010000028af00000002")
        self.assertEqual(ula.avps[3].data, ERROR_DIAGNOSTIC_ODB_ALL_APN)

        self.assertEqual(ula.avps[4].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(ula.avps[4].dump().hex(), "000001154000000c00000001")

        self.assertEqual(ula.avps[5].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(ula.avps[5].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[6].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(ula.avps[6].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[7].code, SUPPORTED_FEATURES_AVP_CODE)
        self.assertEqual(ula.avps[7].dump().hex(), "0000027480000038000028af0000010a4000000c000028af0000027580000010000028af000000010000027680000010000028af00000007")

        self.assertEqual(ula.avps[8].code, ULA_FLAGS_AVP_CODE)
        self.assertEqual(ula.avps[8].dump().hex(), "0000057ec0000010000028af00000001")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("ulr:num_answers:roaming_not_allowed"), b'1')
        cdb.decr("ulr:num_answers:roaming_not_allowed")

        self.assertEqual(cdb.get("ulr:num_requests"), b'1')
        cdb.decr("ulr:num_requests")

    def test__ulr_route__8__diameter_error_roaming_not_allowed__odb_hplmn_apn(self):
        #: Create Update-Location-Request with Roamning not allowed due to subscriber provisioned with ODB-HPLMN-APN
        ula = self.ulr(request=Ulr.roaming_not_allowed(self.subscriber_with_odb_hplmn_apn))

        #: Diameter Header
        self.assertEqual(ula.header.version, DIAMETER_VERSION)
        self.assertEqual(ula.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(ula.header.command_code, UPDATE_LOCATION_MESSAGE)
        self.assertEqual(ula.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(ula.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(ula.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(ula.avps[2].code, EXPERIMENTAL_RESULT_AVP_CODE)
        self.assertEqual(ula.avps[2].dump().hex(), "00000129000000200000012a4000000c0000138c0000010a4000000c000028af")
        self.assertEqual(ula.avps[2].experimental_result_code_avp.data, DIAMETER_ERROR_ROAMING_NOT_ALLOWED)

        self.assertEqual(ula.avps[3].code, ERROR_DIAGNOSTIC_AVP_CODE)
        self.assertEqual(ula.avps[3].dump().hex(), "0000064e80000010000028af00000003")
        self.assertEqual(ula.avps[3].data, ERROR_DIAGNOSTIC_ODB_HPLMN_APN)

        self.assertEqual(ula.avps[4].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(ula.avps[4].dump().hex(), "000001154000000c00000001")

        self.assertEqual(ula.avps[5].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(ula.avps[5].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[6].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(ula.avps[6].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[7].code, SUPPORTED_FEATURES_AVP_CODE)
        self.assertEqual(ula.avps[7].dump().hex(), "0000027480000038000028af0000010a4000000c000028af0000027580000010000028af000000010000027680000010000028af00000007")

        self.assertEqual(ula.avps[8].code, ULA_FLAGS_AVP_CODE)
        self.assertEqual(ula.avps[8].dump().hex(), "0000057ec0000010000028af00000001")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("ulr:num_answers:roaming_not_allowed"), b'1')
        cdb.decr("ulr:num_answers:roaming_not_allowed")

        self.assertEqual(cdb.get("ulr:num_requests"), b'1')
        cdb.decr("ulr:num_requests")

    def test__ulr_route__9__diameter_error_roaming_not_allowed__odb_vplmn_apn(self):
        #: Create Update-Location-Request with Roamning not allowed due to subscriber provisioned with ODB-VPLMN-APN
        ula = self.ulr(request=Ulr.roaming_not_allowed(self.subscriber_with_odb_vplmn_apn))

        #: Diameter Header
        self.assertEqual(ula.header.version, DIAMETER_VERSION)
        self.assertEqual(ula.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(ula.header.command_code, UPDATE_LOCATION_MESSAGE)
        self.assertEqual(ula.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(ula.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(ula.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(ula.avps[2].code, EXPERIMENTAL_RESULT_AVP_CODE)
        self.assertEqual(ula.avps[2].dump().hex(), "00000129000000200000012a4000000c0000138c0000010a4000000c000028af")
        self.assertEqual(ula.avps[2].experimental_result_code_avp.data, DIAMETER_ERROR_ROAMING_NOT_ALLOWED)

        self.assertEqual(ula.avps[3].code, ERROR_DIAGNOSTIC_AVP_CODE)
        self.assertEqual(ula.avps[3].dump().hex(), "0000064e80000010000028af00000004")
        self.assertEqual(ula.avps[3].data, ERROR_DIAGNOSTIC_ODB_VPLMN_APN)

        self.assertEqual(ula.avps[4].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(ula.avps[4].dump().hex(), "000001154000000c00000001")

        self.assertEqual(ula.avps[5].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(ula.avps[5].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[6].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(ula.avps[6].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[7].code, SUPPORTED_FEATURES_AVP_CODE)
        self.assertEqual(ula.avps[7].dump().hex(), "0000027480000038000028af0000010a4000000c000028af0000027580000010000028af000000010000027680000010000028af00000007")

        self.assertEqual(ula.avps[8].code, ULA_FLAGS_AVP_CODE)
        self.assertEqual(ula.avps[8].dump().hex(), "0000057ec0000010000028af00000001")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("ulr:num_answers:roaming_not_allowed"), b'1')
        cdb.decr("ulr:num_answers:roaming_not_allowed")

        self.assertEqual(cdb.get("ulr:num_requests"), b'1')
        cdb.decr("ulr:num_requests")

    def test__ulr_route__10__diameter_success__odb_all_apn(self):
        app.testing_answer = CLA(result_code=DIAMETER_SUCCESS)

        #: Create a regular Update-Location-Request with subscriber provisioned with ODB-all-APN
        ula = self.ulr(request=Ulr.regular_with_odb(user_name=self.subscriber_with_odb_all_apn))

        #: Diameter Header
        self.assertEqual(ula.header.version, DIAMETER_VERSION)
        self.assertEqual(ula.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(ula.header.command_code, UPDATE_LOCATION_MESSAGE)
        self.assertEqual(ula.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(ula.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(ula.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(ula.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(ula.avps[2].dump().hex(), "0000010c4000000c000007d1")
        self.assertEqual(ula.avps[2].data, DIAMETER_SUCCESS)

        self.assertEqual(ula.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(ula.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(ula.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(ula.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(ula.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[6].code, SUPPORTED_FEATURES_AVP_CODE)
        self.assertEqual(ula.avps[6].dump().hex(), "0000027480000038000028af0000010a4000000c000028af0000027580000010000028af000000010000027680000010000028af00000007")

        self.assertEqual(ula.avps[7].code, ULA_FLAGS_AVP_CODE)
        self.assertEqual(ula.avps[7].dump().hex(), "0000057ec0000010000028af00000001")

        self.maxDiff = None
        self.assertEqual(ula.avps[8].code, SUBSCRIPTION_DATA_AVP_CODE)
        self.assertEqual(ula.avps[8].dump().hex(), "00000578c0000378000028af000002bdc0000013000028af551200000000f20000000599c0000013000028af550095999999f90000000590c0000010000028af0000000100000591c0000010000028af000000010000000d80000010000028af303830300000059bc000002c000028af00000204c0000010000028af000186a000000203c0000010000028af000186a000000595c00002e8000028af0000058f80000010000028af0000000100000594c0000010000028af0000000000000596c00000b0000028af0000058f80000010000028af00000001000001ed40000010696e7465726e6574000005b080000010000028af0000000000000597c0000038000028af0000040480000010000028af000000090000040a8000001c000028af0000041680000010000028af000000080000059bc000002c000028af00000203c0000010000028af3b9ac9ff00000204c0000010000028af3b9ac9ff00000598c0000010000028af0000000000000596c00000ac000028af0000058f80000010000028af00000003000001ed4000000b6d6d7300000005b080000010000028af0000000000000597c0000038000028af0000040480000010000028af000000090000040a8000001c000028af0000041680000010000028af000000080000059bc000002c000028af00000203c0000010000028af0000010000000204c0000010000028af0000010000000598c0000010000028af0000000000000596c00000b4000028af0000058f80000010000028af00000004000001ed40000013696e7465726e65746c746500000005b080000010000028af0000000200000597c0000038000028af0000040480000010000028af000000090000040a8000001c000028af0000041680000010000028af000000080000059bc000002c000028af00000203c0000010000028af3b9ac9ff00000204c0000010000028af3b9ac9ff00000598c0000010000028af0000000000000596c00000ac000028af0000058f80000010000028af00000338000001ed4000000b696d7300000005b080000010000028af0000000200000597c0000038000028af0000040480000010000028af000000050000040a8000001c000028af0000041680000010000028af000000080000059bc000002c000028af00000203c0000010000028af0000010000000204c0000010000028af0000010000000598c0000010000028af00000000")

        self.assertEqual(ula.avps[8][0].code, MSISDN_AVP_CODE)
        self.assertEqual(ula.avps[8][0].data, bytes.fromhex("551200000000f2"))

        self.assertEqual(ula.avps[8][1].code, STN_SR_AVP_CODE)
        self.assertEqual(ula.avps[8][1].data, bytes.fromhex("550095999999f9"))

        self.assertEqual(ula.avps[8][2].code, SUBSCRIBER_STATUS_AVP_CODE)
        self.assertEqual(ula.avps[8][2].data, SUBSCRIBER_STATUS_OPERATOR_DETERMINED_BARRING)

        self.assertEqual(ula.avps[8][3].code, OPERATOR_DETERMINED_BARRING_AVP_CODE)
        self.assertTrue(ula.avps[8][3].is_bit_set(0))

        self.assertEqual(ula.avps[8][4].code, X_3GPP_CHARGING_CHARACTERISTICS_AVP_CODE)
        self.assertEqual(ula.avps[8][4].data, bytes.fromhex("30383030"))

        self.assertEqual(ula.avps[8][5].code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][5].data, bytes.fromhex("00000204c0000010000028af000186a000000203c0000010000028af000186a0"))
        self.assertEqual(ula.avps[8][5].max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(100000))
        self.assertEqual(ula.avps[8][5].max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(100000))

        self.assertEqual(ula.avps[8][6].code, APN_CONFIGURATION_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].context_identifier_avp.data, convert_to_4_bytes(1))
        self.assertEqual(ula.avps[8][6].all_apn_configurations_included_indicator_avp.code, ALL_APN_CONFIGURATIONS_INCLUDED_INDICATOR_AVP_CODE)
        self.assertEqual(ula.avps[8][6].all_apn_configurations_included_indicator_avp.data, ALL_APN_CONFIGURATIONS_INCLUDED)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.context_identifier_avp.data, convert_to_4_bytes(1))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.service_selection_avp.data, b"internet")
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)

        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.context_identifier_avp.data, convert_to_4_bytes(3))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.service_selection_avp.data, b"mms")
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)

        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.context_identifier_avp.data, convert_to_4_bytes(4))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.service_selection_avp.data, b"internetlte")
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.pdn_type_avp.data, PDN_TYPE_IPV4V6)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)

        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.context_identifier_avp.data, convert_to_4_bytes(824))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.service_selection_avp.data, b"ims")
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.pdn_type_avp.data, PDN_TYPE_IPV4V6)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(5))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("ulr:num_answers:success"), b'1')
        cdb.decr("ulr:num_answers:success")

        self.assertEqual(cdb.get("ulr:num_requests"), b'1')
        cdb.decr("ulr:num_requests")

    def test__ulr_route__11__diameter_success__odb_hplmn_apn(self):
        app.testing_answer = CLA(result_code=DIAMETER_SUCCESS)

        #: Create a regular Update-Location-Request with subscriber provisioned with ODB-HPLMN-APN
        ula = self.ulr(request=Ulr.regular_with_odb(user_name=self.subscriber_with_odb_hplmn_apn))

        #: Diameter Header
        self.assertEqual(ula.header.version, DIAMETER_VERSION)
        self.assertEqual(ula.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(ula.header.command_code, UPDATE_LOCATION_MESSAGE)
        self.assertEqual(ula.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(ula.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(ula.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(ula.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(ula.avps[2].dump().hex(), "0000010c4000000c000007d1")
        self.assertEqual(ula.avps[2].data, DIAMETER_SUCCESS)

        self.assertEqual(ula.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(ula.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(ula.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(ula.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(ula.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[6].code, SUPPORTED_FEATURES_AVP_CODE)
        self.assertEqual(ula.avps[6].dump().hex(), "0000027480000038000028af0000010a4000000c000028af0000027580000010000028af000000010000027680000010000028af00000007")

        self.assertEqual(ula.avps[7].code, ULA_FLAGS_AVP_CODE)
        self.assertEqual(ula.avps[7].dump().hex(), "0000057ec0000010000028af00000001")

        self.maxDiff = None

        self.assertEqual(ula.avps[8].code, SUBSCRIPTION_DATA_AVP_CODE)
        self.assertEqual(ula.avps[8].dump().hex(), "00000578c0000378000028af000002bdc0000013000028af551200000000f30000000599c0000013000028af550095999999f90000000590c0000010000028af0000000100000591c0000010000028af000000020000000d80000010000028af303830300000059bc000002c000028af00000204c0000010000028af000186a000000203c0000010000028af000186a000000595c00002e8000028af0000058f80000010000028af0000000100000594c0000010000028af0000000000000596c00000b0000028af0000058f80000010000028af00000001000001ed40000010696e7465726e6574000005b080000010000028af0000000000000597c0000038000028af0000040480000010000028af000000090000040a8000001c000028af0000041680000010000028af000000080000059bc000002c000028af00000203c0000010000028af3b9ac9ff00000204c0000010000028af3b9ac9ff00000598c0000010000028af0000000000000596c00000ac000028af0000058f80000010000028af00000003000001ed4000000b6d6d7300000005b080000010000028af0000000000000597c0000038000028af0000040480000010000028af000000090000040a8000001c000028af0000041680000010000028af000000080000059bc000002c000028af00000203c0000010000028af0000010000000204c0000010000028af0000010000000598c0000010000028af0000000000000596c00000b4000028af0000058f80000010000028af00000004000001ed40000013696e7465726e65746c746500000005b080000010000028af0000000200000597c0000038000028af0000040480000010000028af000000090000040a8000001c000028af0000041680000010000028af000000080000059bc000002c000028af00000203c0000010000028af3b9ac9ff00000204c0000010000028af3b9ac9ff00000598c0000010000028af0000000000000596c00000ac000028af0000058f80000010000028af00000338000001ed4000000b696d7300000005b080000010000028af0000000200000597c0000038000028af0000040480000010000028af000000050000040a8000001c000028af0000041680000010000028af000000080000059bc000002c000028af00000203c0000010000028af0000010000000204c0000010000028af0000010000000598c0000010000028af00000000")

        self.assertEqual(ula.avps[8][0].code, MSISDN_AVP_CODE)
        self.assertEqual(ula.avps[8][0].data, bytes.fromhex("551200000000f3"))

        self.assertEqual(ula.avps[8][1].code, STN_SR_AVP_CODE)
        self.assertEqual(ula.avps[8][1].data, bytes.fromhex("550095999999f9"))

        self.assertEqual(ula.avps[8][2].code, SUBSCRIBER_STATUS_AVP_CODE)
        self.assertEqual(ula.avps[8][2].data, SUBSCRIBER_STATUS_OPERATOR_DETERMINED_BARRING)

        self.assertEqual(ula.avps[8][3].code, OPERATOR_DETERMINED_BARRING_AVP_CODE)
        self.assertTrue(ula.avps[8][3].is_bit_set(1))

        self.assertEqual(ula.avps[8][4].code, X_3GPP_CHARGING_CHARACTERISTICS_AVP_CODE)
        self.assertEqual(ula.avps[8][4].data, bytes.fromhex("30383030"))

        self.assertEqual(ula.avps[8][5].code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][5].data, bytes.fromhex("00000204c0000010000028af000186a000000203c0000010000028af000186a0"))
        self.assertEqual(ula.avps[8][5].max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(100000))
        self.assertEqual(ula.avps[8][5].max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(100000))

        self.assertEqual(ula.avps[8][6].code, APN_CONFIGURATION_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].context_identifier_avp.data, convert_to_4_bytes(1))
        self.assertEqual(ula.avps[8][6].all_apn_configurations_included_indicator_avp.code, ALL_APN_CONFIGURATIONS_INCLUDED_INDICATOR_AVP_CODE)
        self.assertEqual(ula.avps[8][6].all_apn_configurations_included_indicator_avp.data, ALL_APN_CONFIGURATIONS_INCLUDED)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.context_identifier_avp.data, convert_to_4_bytes(1))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.service_selection_avp.data, b"internet")
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)

        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.context_identifier_avp.data, convert_to_4_bytes(3))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.service_selection_avp.data, b"mms")
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)

        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.context_identifier_avp.data, convert_to_4_bytes(4))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.service_selection_avp.data, b"internetlte")
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.pdn_type_avp.data, PDN_TYPE_IPV4V6)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)

        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.context_identifier_avp.data, convert_to_4_bytes(824))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.service_selection_avp.data, b"ims")
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.pdn_type_avp.data, PDN_TYPE_IPV4V6)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(5))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("ulr:num_answers:success"), b'1')
        cdb.decr("ulr:num_answers:success")

        self.assertEqual(cdb.get("ulr:num_requests"), b'1')
        cdb.decr("ulr:num_requests")

    def test__ulr_route__12__diameter_success__odb_vplmn_apn(self):
        app.testing_answer = CLA(result_code=DIAMETER_SUCCESS)

        #: Create a regular Update-Location-Request with subscriber provisioned with ODB-VPLMN-APN
        ula = self.ulr(request=Ulr.regular_with_odb(user_name=self.subscriber_with_odb_vplmn_apn))

        #: Diameter Header
        self.assertEqual(ula.header.version, DIAMETER_VERSION)
        self.assertEqual(ula.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(ula.header.command_code, UPDATE_LOCATION_MESSAGE)
        self.assertEqual(ula.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(ula.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(ula.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(ula.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(ula.avps[2].dump().hex(), "0000010c4000000c000007d1")
        self.assertEqual(ula.avps[2].data, DIAMETER_SUCCESS)

        self.assertEqual(ula.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(ula.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(ula.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(ula.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(ula.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[6].code, SUPPORTED_FEATURES_AVP_CODE)
        self.assertEqual(ula.avps[6].dump().hex(), "0000027480000038000028af0000010a4000000c000028af0000027580000010000028af000000010000027680000010000028af00000007")

        self.assertEqual(ula.avps[7].code, ULA_FLAGS_AVP_CODE)
        self.assertEqual(ula.avps[7].dump().hex(), "0000057ec0000010000028af00000001")

        self.maxDiff = None

        self.assertEqual(ula.avps[8].code, SUBSCRIPTION_DATA_AVP_CODE)
        self.assertEqual(ula.avps[8].dump().hex(), "00000578c0000378000028af000002bdc0000013000028af551200000000f40000000599c0000013000028af550095999999f90000000590c0000010000028af0000000100000591c0000010000028af000000040000000d80000010000028af303830300000059bc000002c000028af00000204c0000010000028af000186a000000203c0000010000028af000186a000000595c00002e8000028af0000058f80000010000028af0000000100000594c0000010000028af0000000000000596c00000b0000028af0000058f80000010000028af00000001000001ed40000010696e7465726e6574000005b080000010000028af0000000000000597c0000038000028af0000040480000010000028af000000090000040a8000001c000028af0000041680000010000028af000000080000059bc000002c000028af00000203c0000010000028af3b9ac9ff00000204c0000010000028af3b9ac9ff00000598c0000010000028af0000000000000596c00000ac000028af0000058f80000010000028af00000003000001ed4000000b6d6d7300000005b080000010000028af0000000000000597c0000038000028af0000040480000010000028af000000090000040a8000001c000028af0000041680000010000028af000000080000059bc000002c000028af00000203c0000010000028af0000010000000204c0000010000028af0000010000000598c0000010000028af0000000000000596c00000b4000028af0000058f80000010000028af00000004000001ed40000013696e7465726e65746c746500000005b080000010000028af0000000200000597c0000038000028af0000040480000010000028af000000090000040a8000001c000028af0000041680000010000028af000000080000059bc000002c000028af00000203c0000010000028af3b9ac9ff00000204c0000010000028af3b9ac9ff00000598c0000010000028af0000000000000596c00000ac000028af0000058f80000010000028af00000338000001ed4000000b696d7300000005b080000010000028af0000000200000597c0000038000028af0000040480000010000028af000000050000040a8000001c000028af0000041680000010000028af000000080000059bc000002c000028af00000203c0000010000028af0000010000000204c0000010000028af0000010000000598c0000010000028af00000000")

        self.assertEqual(ula.avps[8][0].code, MSISDN_AVP_CODE)
        self.assertEqual(ula.avps[8][0].data, bytes.fromhex("551200000000f4"))

        self.assertEqual(ula.avps[8][1].code, STN_SR_AVP_CODE)
        self.assertEqual(ula.avps[8][1].data, bytes.fromhex("550095999999f9"))

        self.assertEqual(ula.avps[8][2].code, SUBSCRIBER_STATUS_AVP_CODE)
        self.assertEqual(ula.avps[8][2].data, SUBSCRIBER_STATUS_OPERATOR_DETERMINED_BARRING)

        self.assertEqual(ula.avps[8][3].code, OPERATOR_DETERMINED_BARRING_AVP_CODE)
        self.assertTrue(ula.avps[8][3].is_bit_set(2))

        self.assertEqual(ula.avps[8][4].code, X_3GPP_CHARGING_CHARACTERISTICS_AVP_CODE)
        self.assertEqual(ula.avps[8][4].data, bytes.fromhex("30383030"))

        self.assertEqual(ula.avps[8][5].code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][5].data, bytes.fromhex("00000204c0000010000028af000186a000000203c0000010000028af000186a0"))
        self.assertEqual(ula.avps[8][5].max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(100000))
        self.assertEqual(ula.avps[8][5].max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][5].max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(100000))

        self.assertEqual(ula.avps[8][6].code, APN_CONFIGURATION_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].context_identifier_avp.data, convert_to_4_bytes(1))
        self.assertEqual(ula.avps[8][6].all_apn_configurations_included_indicator_avp.code, ALL_APN_CONFIGURATIONS_INCLUDED_INDICATOR_AVP_CODE)
        self.assertEqual(ula.avps[8][6].all_apn_configurations_included_indicator_avp.data, ALL_APN_CONFIGURATIONS_INCLUDED)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.context_identifier_avp.data, convert_to_4_bytes(1))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.service_selection_avp.data, b"internet")
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)

        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.context_identifier_avp.data, convert_to_4_bytes(3))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.service_selection_avp.data, b"mms")
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.pdn_type_avp.data, PDN_TYPE_IPV4)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__1.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)

        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.context_identifier_avp.data, convert_to_4_bytes(4))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.service_selection_avp.data, b"internetlte")
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.pdn_type_avp.data, PDN_TYPE_IPV4V6)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(9))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(999999999))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__2.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)

        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.context_identifier_avp.code, CONTEXT_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.code, APN_CONFIGURATION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.context_identifier_avp.data, convert_to_4_bytes(824))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.service_selection_avp.code, SERVICE_SELECTION_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.service_selection_avp.data, b"ims")
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.pdn_type_avp.code, PDN_TYPE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.pdn_type_avp.data, PDN_TYPE_IPV4V6)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.code, EPS_SUBSCRIBED_QOS_PROFILE_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.code, QOS_CLASS_IDENTIFIER_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.qos_class_identifier_avp.data, convert_to_4_bytes(5))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.code, ALLOCATION_RETENTION_PRIORITY_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.code, PRIORITY_LEVEL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.eps_subscribed_qos_profile_avp.allocation_retention_priority_avp.priority_level_avp.data, convert_to_4_bytes(8))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.ambr_avp.code, AMBR_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_dl_avp.code, MAX_REQUESTED_BANDWIDTH_DL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_dl_avp.data, convert_to_4_bytes(256))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_ul_avp.code, MAX_REQUESTED_BANDWIDTH_UL_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.ambr_avp.max_requested_bandwidth_ul_avp.data, convert_to_4_bytes(256))
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.vplmn_dynamic_address_allowed_avp.code, VPLMN_DYNAMIC_ADDRESS_ALLOWED_AVP_CODE)
        self.assertEqual(ula.avps[8][6].apn_configuration_avp__3.vplmn_dynamic_address_allowed_avp.data, VPLMN_DYNAMIC_ADDRESS_ALLOWED_NOT_ALLOWED)

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("ulr:num_answers:success"), b'1')
        cdb.decr("ulr:num_answers:success")

        self.assertEqual(cdb.get("ulr:num_requests"), b'1')
        cdb.decr("ulr:num_requests")

    def test__ulr_route__13__diameter_realm_not_served(self):
        app.testing_answer = CLA(result_code=DIAMETER_SUCCESS)

        #: Create Update-Location-Request with realm not served
        ula = self.ulr(request=Ulr.realm_not_served("999000000000004"))

        #: Diameter Header
        self.assertEqual(ula.header.version, DIAMETER_VERSION)
        self.assertEqual(ula.header.flags, FLAG_RESPONSE_AND_PROXYABLE)
        self.assertEqual(ula.header.command_code, UPDATE_LOCATION_MESSAGE)
        self.assertEqual(ula.header.application_id, DIAMETER_APPLICATION_S6a)

        #: Diameter AVPs
        self.assertEqual(ula.avps[1].code, VENDOR_SPECIFIC_APPLICATION_ID_AVP_CODE)
        self.assertEqual(ula.avps[1].dump().hex(), "00000104400000200000010a4000000c000028af000001024000000c01000023")

        self.assertEqual(ula.avps[2].code, RESULT_CODE_AVP_CODE)
        self.assertEqual(ula.avps[2].dump().hex(), "0000010c4000000c00000bbb")
        self.assertEqual(ula.avps[2].data, DIAMETER_REALM_NOT_SERVED)

        self.assertEqual(ula.avps[3].code, AUTH_SESSION_STATE_AVP_CODE)
        self.assertEqual(ula.avps[3].dump().hex(), "000001154000000c00000001")

        self.assertEqual(ula.avps[4].code, ORIGIN_HOST_AVP_CODE)
        self.assertEqual(ula.avps[4].dump().hex(), "000001084000001d6873732e6570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[5].code, ORIGIN_REALM_AVP_CODE)
        self.assertEqual(ula.avps[5].dump().hex(), "00000128400000196570632e6d796e6574776f726b2e636f6d000000")

        self.assertEqual(ula.avps[6].code, SUPPORTED_FEATURES_AVP_CODE)
        self.assertEqual(ula.avps[6].dump().hex(), "0000027480000038000028af0000010a4000000c000028af0000027580000010000028af000000010000027680000010000028af00000007")

        self.assertEqual(ula.avps[7].code, ULA_FLAGS_AVP_CODE)
        self.assertEqual(ula.avps[7].dump().hex(), "0000057ec0000010000028af00000001")

        self.assertEqual(ula.avps[8].code, ERROR_MESSAGE_AVP_CODE)
        self.assertEqual(ula.avps[8].dump().hex(), "00000119000000584f726967696e2d5265616c6d2041565020646f6573206e6f7420636f6d706c792077697468203347505020666f726d61743a206d6e634d4e432e6d63634d43432e336770706e6574776f726b2e6f7267")
        self.assertEqual(ula.avps[8].data, b"Origin-Realm AVP does not comply with 3GPP format: mncMNC.mccMCC.3gppnetwork.org")

        #: Check if Cache has been updated
        self.assertEqual(cdb.get("ulr:num_answers:realm_not_served"), b'1')
        cdb.decr("ulr:num_answers:realm_not_served")

        self.assertEqual(cdb.get("ulr:num_requests"), b'1')
        cdb.decr("ulr:num_requests")


if __name__ == "__main__":
    unittest.main()