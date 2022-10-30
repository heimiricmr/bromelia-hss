# -*- coding: utf-8 -*-
"""
    hss_provisioning.tests.test_routes
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module contains the Bromelia-HSS Provisioning app's routes unittests.
    
    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

import json
import os
import sys
import unittest

import requests

testing_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(testing_dir)

sys.path.insert(0, base_dir)

from constants import *


# @unittest.skip
class TestApnCreateEndpointWithInvalidInputs(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:5001/apns"
        self.content = {
            "apn_id": 10000,
            "apn_name": "internet",
            "pdn_type": "IPv4v6",
            "qci": 9,
            "priority_level": 8,
            "max_req_bw_ul": 999999999,
            "max_req_bw_dl": 999999999
        }

    def test__required_parameter_not_included__apn_id(self):
        #: Remove property
        apn_id = self.content["apn_id"]
        self.content.pop("apn_id")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'apn_id' is a required property", r_content["error_message"])

        #: Add property back
        self.content.update({"apn_id": apn_id})

    def test__required_parameter_not_included__apn_name(self):
        #: Remove property
        apn_name = self.content["apn_name"]
        self.content.pop("apn_name")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'apn_name' is a required property", r_content["error_message"])
        
        #: Add property back 
        self.content.update({"apn_name": apn_name})

    def test__required_parameter_not_included__pdn_type(self):
        #: Remove property
        pdn_type = self.content["pdn_type"]
        self.content.pop("pdn_type")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'pdn_type' is a required property", r_content["error_message"])
        
        #: Add property back 
        self.content.update({"pdn_type": pdn_type})

    def test__required_parameter_not_included__qci(self):
        #: Remove property
        qci = self.content["qci"]
        self.content.pop("qci")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'qci' is a required property", r_content["error_message"])
        
        #: Add property back 
        self.content.update({"qci": qci})

    def test__required_parameter_not_included__priority_level(self):
        #: Remove property
        priority_level = self.content["priority_level"]
        self.content.pop("priority_level")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'priority_level' is a required property", r_content["error_message"])
        
        #: Add property back 
        self.content.update({"priority_level": priority_level})

    def test__required_parameter_not_included__max_req_bw_ul(self):
        #: Remove property
        max_req_bw_ul = self.content["max_req_bw_ul"]
        self.content.pop("max_req_bw_ul")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'max_req_bw_ul' is a required property", r_content["error_message"])
        
        #: Add property back 
        self.content.update({"max_req_bw_ul": max_req_bw_ul})

    def test__required_parameter_not_included__max_req_bw_dl(self):
        #: Remove property
        max_req_bw_dl = self.content["max_req_bw_dl"]
        self.content.pop("max_req_bw_dl")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'max_req_bw_dl' is a required property", r_content["error_message"])
        
        #: Add property back 
        self.content.update({"max_req_bw_dl": max_req_bw_dl})

    def test__required_parameter_with_invalid_value__apn_id__list(self):
        #: Remove property and Add again with invalid value
        apn_id = self.content["apn_id"]
        self.content.pop("apn_id")
        self.content.update({"apn_id": [apn_id]})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'integer'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['apn_id']", r_content["error_message"])

        #: Add property with valid type back 
        self.content.pop("apn_id")
        self.content.update({"apn_id": apn_id})

    def test__required_parameter_with_invalid_value__apn_id__string(self):
        #: Remove property and Add again with invalid value
        apn_id = self.content["apn_id"]
        self.content.pop("apn_id")
        self.content.update({"apn_id": "apn_id"})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'integer'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['apn_id']", r_content["error_message"])

        #: Add property with valid type back 
        self.content.pop("apn_id")
        self.content.update({"apn_id": apn_id})

    def test__required_parameter_with_invalid_value__apn_name__list(self):
        #: Remove property and Add again with invalid value
        apn_name = self.content["apn_name"]
        self.content.pop("apn_name")
        self.content.update({"apn_name": [apn_name]})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'string'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['apn_name']", r_content["error_message"])

        #: Add property with valid type back 
        self.content.pop("apn_name")
        self.content.update({"apn_name": apn_name})

    def test__required_parameter_with_invalid_value__apn_name__integer(self):
        #: Remove property and Add again with invalid value
        apn_name = self.content["apn_name"]
        self.content.pop("apn_name")
        self.content.update({"apn_name": 1992})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'string'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['apn_name']", r_content["error_message"])

        #: Add property with valid type back 
        self.content.pop("apn_name")
        self.content.update({"apn_name": apn_name})

    def test__required_parameter_with_invalid_value__pdn_type__list(self):
        #: Remove property and Add again with invalid value
        pdn_type = self.content["pdn_type"]
        self.content.pop("pdn_type")
        self.content.update({"pdn_type": [pdn_type]})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'string'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['pdn_type']", r_content["error_message"])

        #: Add property with valid type back 
        self.content.pop("pdn_type")
        self.content.update({"pdn_type": pdn_type})

    def test__required_parameter_with_invalid_value__pdn_type__integer(self):
        #: Remove property and Add again with invalid value
        pdn_type = self.content["pdn_type"]
        self.content.pop("pdn_type")
        self.content.update({"pdn_type": 1992})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'string'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['pdn_type']", r_content["error_message"])

        #: Add property with valid type back 
        self.content.pop("pdn_type")
        self.content.update({"pdn_type": pdn_type})

    def test__required_parameter_with_invalid_value__qci__list(self):
        #: Remove property and Add again with invalid value
        qci = self.content["qci"]
        self.content.pop("qci")
        self.content.update({"qci": [qci]})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'integer'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['qci']", r_content["error_message"])

        #: Add property with valid type back 
        self.content.pop("qci")
        self.content.update({"qci": qci})

    def test__required_parameter_with_invalid_value__qci__string(self):
        #: Remove property and Add again with invalid value
        qci = self.content["qci"]
        self.content.pop("qci")
        self.content.update({"qci": "qci"})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'integer'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['qci']", r_content["error_message"])

        #: Add property with valid type back 
        self.content.pop("qci")
        self.content.update({"qci": qci})

    def test__required_parameter_with_invalid_value__priority_level__list(self):
        #: Remove property and Add again with invalid value
        priority_level = self.content["priority_level"]
        self.content.pop("priority_level")
        self.content.update({"priority_level": [priority_level]})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'integer'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['priority_level']", r_content["error_message"])

        #: Add property with valid type back 
        self.content.pop("priority_level")
        self.content.update({"priority_level": priority_level})

    def test__required_parameter_with_invalid_value__priority_level__string(self):
        #: Remove property and Add again with invalid value
        priority_level = self.content["priority_level"]
        self.content.pop("priority_level")
        self.content.update({"priority_level": "priority_level"})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'integer'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['priority_level']", r_content["error_message"])

        #: Add property with valid type back 
        self.content.pop("priority_level")
        self.content.update({"priority_level": priority_level})

    def test__required_parameter_with_invalid_value__max_req_bw_ul__list(self):
        #: Remove property and Add again with invalid value
        max_req_bw_ul = self.content["max_req_bw_ul"]
        self.content.pop("max_req_bw_ul")
        self.content.update({"max_req_bw_ul": [max_req_bw_ul]})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'integer'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['max_req_bw_ul']", r_content["error_message"])

        #: Add property with valid type back 
        self.content.pop("max_req_bw_ul")
        self.content.update({"max_req_bw_ul": max_req_bw_ul})

    def test__required_parameter_with_invalid_value__max_req_bw_ul__string(self):
        #: Remove property and Add again with invalid value
        max_req_bw_ul = self.content["max_req_bw_ul"]
        self.content.pop("max_req_bw_ul")
        self.content.update({"max_req_bw_ul": "max_req_bw_ul"})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'integer'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['max_req_bw_ul']", r_content["error_message"])

        #: Add property with valid type back 
        self.content.pop("max_req_bw_ul")
        self.content.update({"max_req_bw_ul": max_req_bw_ul})

    def test__required_parameter_with_invalid_value__max_req_bw_dl__list(self):
        #: Remove property and Add again with invalid value
        max_req_bw_dl = self.content["max_req_bw_dl"]
        self.content.pop("max_req_bw_dl")
        self.content.update({"max_req_bw_dl": [max_req_bw_dl]})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'integer'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['max_req_bw_dl']", r_content["error_message"])

        #: Add property with valid type back 
        self.content.pop("max_req_bw_dl")
        self.content.update({"max_req_bw_dl": max_req_bw_dl})

    def test__required_parameter_with_invalid_value__max_req_bw_dl__string(self):
        #: Remove property and Add again with invalid value
        max_req_bw_dl = self.content["max_req_bw_dl"]
        self.content.pop("max_req_bw_dl")
        self.content.update({"max_req_bw_dl": "max_req_bw_dl"})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'integer'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['max_req_bw_dl']", r_content["error_message"])

        #: Add property with valid type back 
        self.content.pop("max_req_bw_dl")
        self.content.update({"max_req_bw_dl": max_req_bw_dl})


# @unittest.skip
class TestSubscriberCreateEndpointWithInvalidInputs(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:5001/subscribers"
        self.content = {
            "identities": {
                "imsi": "999000000000011",
                "msisdn": "5521000000011"
            },
            "auth": {
                "key": "465b5ce8b199b49faa5f0a2ee238a6bc",
                "opc": "013d7d16d7ad4fefb61bd95b765c8ceb",
                "amf": "b9b9",
                "sqn": "ff9bb4d0b607"
            },
            "subscription": {
                "stn_sr": "5500599999999",
                "odb": "ODB-VPLMN-APN",
                "roaming_allowed": False,
                "schar": 8,
                "max_req_bw_ul": 256,
                "max_req_bw_dl": 256,
                "default_apn": 824,
                "apns": [
                    4,
                    3,
                    824
                ]
            }
        }

    def test__required_parameter_not_included__identities(self):
        #: Remove property
        identities = self.content["identities"]
        self.content.pop("identities")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'identities' is a required property", r_content["error_message"])

        #: Add property back
        self.content.update({"identities": identities})

    def test__required_parameter_not_included__identities_imsi(self):
        #: Remove property
        imsi = self.content["identities"]["imsi"]
        self.content["identities"].pop("imsi")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'imsi' is a required property", r_content["error_message"])

        #: Add property back
        self.content["identities"].update({"imsi": imsi})

    def test__required_parameter_not_included__identities_msisdn(self):
        #: Remove property
        msisdn = self.content["identities"]["msisdn"]
        self.content["identities"].pop("msisdn")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'msisdn' is a required property", r_content["error_message"])

        #: Add property back
        self.content["identities"].update({"msisdn": msisdn})

    def test__required_parameter_not_included__auth(self):
        #: Remove property
        auth = self.content["auth"]
        self.content.pop("auth")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'auth' is a required property", r_content["error_message"])

        #: Add property back
        self.content.update({"auth": auth})

    def test__required_parameter_not_included__auth_key(self):
        #: Remove property
        key = self.content["auth"]["key"]
        self.content["auth"].pop("key")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'key' is a required property", r_content["error_message"])

        #: Add property back
        self.content["auth"].update({"key": key})

    def test__required_parameter_not_included__auth_opc(self):
        #: Remove property
        opc = self.content["auth"]["opc"]
        self.content["auth"].pop("opc")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'opc' is a required property", r_content["error_message"])

        #: Add property back
        self.content["auth"].update({"opc": opc})

    def test__required_parameter_not_included__auth_amf(self):
        #: Remove property
        amf = self.content["auth"]["amf"]
        self.content["auth"].pop("amf")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'amf' is a required property", r_content["error_message"])

        #: Add property back
        self.content["auth"].update({"amf": amf})

    def test__required_parameter_not_included__auth_sqn(self):
        #: Remove property
        sqn = self.content["auth"]["sqn"]
        self.content["auth"].pop("sqn")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'sqn' is a required property", r_content["error_message"])

        #: Add property back
        self.content["auth"].update({"sqn": sqn})

    def test__required_parameter_not_included__subscription(self):
        #: Remove property
        subscription = self.content["subscription"]
        self.content.pop("subscription")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'subscription' is a required property", r_content["error_message"])

        #: Add property back
        self.content.update({"subscription": subscription})

    def test__required_parameter_not_included__subscription_schar(self):
        #: Remove property
        schar = self.content["subscription"]["schar"]
        self.content["subscription"].pop("schar")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'schar' is a required property", r_content["error_message"])

        #: Add property back
        self.content["subscription"].update({"schar": schar})

    def test__required_parameter_not_included__subscription_default_apn(self):
        #: Remove property
        default_apn = self.content["subscription"]["default_apn"]
        self.content["subscription"].pop("default_apn")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'default_apn' is a required property", r_content["error_message"])

        #: Add property back
        self.content["subscription"].update({"default_apn": default_apn})

    def test__required_parameter_not_included__subscription_apns(self):
        #: Remove property
        apns = self.content["subscription"]["apns"]
        self.content["subscription"].pop("apns")

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("'apns' is a required property", r_content["error_message"])

        #: Add property back
        self.content["subscription"].update({"apns": apns})

    def test__required_parameter_with_invalid_value__identities_imsi__list(self):
        #: Remove property and Add again with invalid value
        imsi = self.content["identities"]["imsi"]
        self.content["identities"].pop("imsi")
        self.content["identities"].update({"imsi": [imsi]})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'string'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['identities']['properties']['imsi']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["identities"].pop("imsi")
        self.content["identities"].update({"imsi": imsi})

    def test__required_parameter_with_invalid_value__identities_imsi__integer(self):
        #: Remove property and Add again with invalid value
        imsi = self.content["identities"]["imsi"]
        self.content["identities"].pop("imsi")
        self.content["identities"].update({"imsi": int(imsi)})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'string'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['identities']['properties']['imsi']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["identities"].pop("imsi")
        self.content["identities"].update({"imsi": imsi})

    def test__required_parameter_with_invalid_value__identities_msisdn__list(self):
        #: Remove property and Add again with invalid value
        msisdn = self.content["identities"]["msisdn"]
        self.content["identities"].pop("msisdn")
        self.content["identities"].update({"msisdn": [msisdn]})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'string'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['identities']['properties']['msisdn']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["identities"].pop("msisdn")
        self.content["identities"].update({"msisdn": msisdn})

    def test__required_parameter_with_invalid_value__identities_msisdn__integer(self):
        #: Remove property and Add again with invalid value
        msisdn = self.content["identities"]["msisdn"]
        self.content["identities"].pop("msisdn")
        self.content["identities"].update({"msisdn": int(msisdn)})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'string'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['identities']['properties']['msisdn']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["identities"].pop("msisdn")
        self.content["identities"].update({"msisdn": msisdn})

    def test__required_parameter_with_invalid_value__auth_key__list(self):
        #: Remove property and Add again with invalid value
        key = self.content["auth"]["key"]
        self.content["auth"].pop("key")
        self.content["auth"].update({"key": [key]})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'string'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['auth']['properties']['key']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["auth"].pop("key")
        self.content["auth"].update({"key": key})

    def test__required_parameter_with_invalid_value__auth_key__integer(self):
        #: Remove property and Add again with invalid value
        key = self.content["auth"]["key"]
        self.content["auth"].pop("key")
        self.content["auth"].update({"key": 1992})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'string'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['auth']['properties']['key']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["auth"].pop("key")
        self.content["auth"].update({"key": key})

    def test__required_parameter_with_invalid_value__auth_opc__list(self):
        #: Remove property and Add again with invalid value
        opc = self.content["auth"]["opc"]
        self.content["auth"].pop("opc")
        self.content["auth"].update({"opc": [opc]})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'string'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['auth']['properties']['opc']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["auth"].pop("opc")
        self.content["auth"].update({"opc": opc})

    def test__required_parameter_with_invalid_value__auth_opc__integer(self):
        #: Remove property and Add again with invalid value
        opc = self.content["auth"]["opc"]
        self.content["auth"].pop("opc")
        self.content["auth"].update({"opc": 1992})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'string'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['auth']['properties']['opc']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["auth"].pop("opc")
        self.content["auth"].update({"opc": opc})

    def test__required_parameter_with_invalid_value__auth_amf__list(self):
        #: Remove property and Add again with invalid value
        amf = self.content["auth"]["amf"]
        self.content["auth"].pop("amf")
        self.content["auth"].update({"amf": [amf]})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'string'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['auth']['properties']['amf']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["auth"].pop("amf")
        self.content["auth"].update({"amf": amf})

    def test__required_parameter_with_invalid_value__auth_amf__integer(self):
        #: Remove property and Add again with invalid value
        amf = self.content["auth"]["amf"]
        self.content["auth"].pop("amf")
        self.content["auth"].update({"amf": 1992})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'string'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['auth']['properties']['amf']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["auth"].pop("amf")
        self.content["auth"].update({"amf": amf})

    def test__required_parameter_with_invalid_value__auth_sqn__list(self):
        #: Remove property and Add again with invalid value
        sqn = self.content["auth"]["sqn"]
        self.content["auth"].pop("sqn")
        self.content["auth"].update({"sqn": [sqn]})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'string'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['auth']['properties']['sqn']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["auth"].pop("sqn")
        self.content["auth"].update({"sqn": sqn})

    def test__required_parameter_with_invalid_value__auth_sqn__integer(self):
        #: Remove property and Add again with invalid value
        sqn = self.content["auth"]["sqn"]
        self.content["auth"].pop("sqn")
        self.content["auth"].update({"sqn": 1992})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'string'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['auth']['properties']['sqn']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["auth"].pop("sqn")
        self.content["auth"].update({"sqn": sqn})

    def test__required_parameter_with_invalid_value__subscription_schar__list(self):
        #: Remove property and Add again with invalid value
        schar = self.content["subscription"]["schar"]
        self.content["subscription"].pop("schar")
        self.content["subscription"].update({"schar": [schar]})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'integer'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['subscription']['properties']['schar']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["subscription"].pop("schar")
        self.content["subscription"].update({"schar": schar})

    def test__required_parameter_with_invalid_value__subscription_schar__string(self):
        #: Remove property and Add again with invalid value
        schar = self.content["subscription"]["schar"]
        self.content["subscription"].pop("schar")
        self.content["subscription"].update({"schar": str(schar)})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'integer'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['subscription']['properties']['schar']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["subscription"].pop("schar")
        self.content["subscription"].update({"schar": schar})

    def test__required_parameter_with_invalid_value__subscription_default_apn__list(self):
        #: Remove property and Add again with invalid value
        default_apn = self.content["subscription"]["default_apn"]
        self.content["subscription"].pop("default_apn")
        self.content["subscription"].update({"default_apn": [default_apn]})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'integer'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['subscription']['properties']['default_apn']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["subscription"].pop("default_apn")
        self.content["subscription"].update({"default_apn": default_apn})

    def test__required_parameter_with_invalid_value__subscription_default_apn__string(self):
        #: Remove property and Add again with invalid value
        default_apn = self.content["subscription"]["default_apn"]
        self.content["subscription"].pop("default_apn")
        self.content["subscription"].update({"default_apn": str(default_apn)})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'integer'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['subscription']['properties']['default_apn']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["subscription"].pop("default_apn")
        self.content["subscription"].update({"default_apn": default_apn})

    def test__required_parameter_with_invalid_value__subscription_apns__integer(self):
        #: Remove property and Add again with invalid value
        apns = self.content["subscription"]["apns"]
        self.content["subscription"].pop("apns")
        self.content["subscription"].update({"apns": 1992})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'array'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['subscription']['properties']['apns']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["subscription"].pop("apns")
        self.content["subscription"].update({"apns": apns})

    def test__required_parameter_with_invalid_value__subscription_apns__string(self):
        #: Remove property and Add again with invalid value
        apns = self.content["subscription"]["apns"]
        self.content["subscription"].pop("apns")
        self.content["subscription"].update({"apns": str(apns)})

        #: Call API and extract JSON response
        r = requests.post(
            self.base_url, 
            data=json.dumps(self.content), 
            headers={"Content-Type": "application/json"}
        )
        r_content = json.loads(r.content.decode("utf-8"))

        #: Check status code and error message
        self.assertEqual(r.status_code, HTTP_400_BAD_REQUEST)
        self.assertIn("is not of type 'array'", r_content["error_message"])
        self.assertIn("Failed validating 'type' in schema['properties']['subscription']['properties']['apns']", r_content["error_message"])

        #: Add property with valid type back 
        self.content["subscription"].pop("apns")
        self.content["subscription"].update({"apns": apns})


# @unittest.skip
class TestApnLifecycle(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:5001/apns"

    def test__only_one_apn(self):
        #: Setup variables
        apn_id = 10000
        resource_url = f"{self.base_url}/{apn_id}"

        content = {
            "apn_id": apn_id,
            "apn_name": "internet",
            "pdn_type": "IPv4v6",
            "qci": 9,
            "priority_level": 8,
            "max_req_bw_ul": 999999999,
            "max_req_bw_dl": 999999999
        }

        #: Create APN
        r = requests.post(
            self.base_url, 
            data=json.dumps(content), 
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(r.status_code, HTTP_201_CREATED)

        #: Read APN
        r = requests.get(resource_url)

        r_content = json.loads(r.content.decode("utf-8"))
        r_content.pop("id")

        self.assertEqual(r.status_code, HTTP_200_OK)
        self.assertEqual(r_content, content)

        #: Delete APN
        r = requests.delete(resource_url)
        self.assertEqual(r.status_code, HTTP_204_NO_CONTENT)


# @unittest.skip
class TestSubscriberLifecycle(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://localhost:5001/subscribers"

    def test__only_one_subscriber(self):
        #: Setup variables
        imsi = "999000000000999"
        msisdn = "5521000000999"

        resource_url = f"{self.base_url}/imsi/{imsi}"

        content = {
            "identities": {
                "imsi": imsi,
                "msisdn": msisdn
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
            self.base_url, 
            data=json.dumps(content), 
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(r.status_code, HTTP_201_CREATED)

        #: Read Subscriber
        r = requests.get(resource_url)

        r_content = json.loads(r.content.decode("utf-8"))

        self.maxDiff = None
        self.assertEqual(r.status_code, HTTP_200_OK)
        # self.assertEqual(r_content, content)

        #: Delete Subscriber
        r = requests.delete(resource_url)
        self.assertEqual(r.status_code, HTTP_204_NO_CONTENT)
