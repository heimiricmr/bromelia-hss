# -*- coding: utf-8 -*-
"""
    hss_provisioning.utils
    ~~~~~~~~~~~~~~~~~~~~~~

    This module contains supporting functions.
    
    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

import json
import re

from flask import (
	jsonify,
	make_response
)
from jsonschema import validate

from constants import *
from config import Config


def get_json_content(request):
    #: Verify if incoming request data extension is JSON text.
    if not request.is_json:
        raise Exception

    content = request.data.decode("utf-8")

    #: Verify if incoming request data content complies to JSON RFC 7159.
    return json.loads(content)


def is_imsi(subscription_id):
    pattern = re.findall(r"^[0-9]{15}$", str(subscription_id))
    if pattern:
        return True
    return False


def is_msisdn(subscription_id):
    pattern = re.findall(r"^[0-9]{13}$", str(subscription_id))
    if pattern:
        return True
    return False


def schema_validation(transaction, transaction_type):
	""" Schema Validation. This function checks if either HLR API Request or 
	HLR API Response is valid as per JSON API Schema.
	"""

	if (transaction_type == "subscriber-request"):
		schema = Config.request_schema_subscriber

	elif (transaction_type == "subscriber-response"):
		schema = Config.response_schema_subscriber

	if (transaction_type == "apn-request"):
		schema = Config.request_schema_apn

	try:
		validate(transaction, schema)
		return {
			"is_valid": True
		}
	
	except Exception as error:
		return {
			"is_valid": False,
			"message": str(error),
		}


def is_response_valid(response_transaction):
	""" Is Response Valid?. This function checks if HLR API Response is valid 
	as per JSON API Schema.
	"""
	return schema_validation(response_transaction, "response")["is_valid"]
		

class Parser():
	def __init__(self, request, transaction_type):
		self.request = request
		self.profile = None
		self.request_schema_validation = schema_validation(self.request, transaction_type)

	def is_valid(self):
		return self.request_schema_validation["is_valid"]

	def get_error_message(self):
		return self.request_schema_validation["message"]


class SubscriberParser(Parser):
	def __init__(self, request):
		super().__init__(request, "subscriber-request")

	def is_valid(self):
		if self.request_schema_validation["is_valid"]:
			if "stn_sr" in self.request["subscription"]:
				stn_sr = int(self.request["subscription"]["stn_sr"])
			else:
				stn_sr = None

			if "odb" in self.request["subscription"]:
				odb = self.request["subscription"]["odb"]
			else:
				odb = None

			if "roaming_allowed" in self.request["subscription"]:
				roaming_allowed = int(self.request["subscription"]["roaming_allowed"])
			else:
				roaming_allowed = None

			if "max_req_bw_ul" in self.request["subscription"]:
				max_req_bw_ul = int(self.request["subscription"]["max_req_bw_ul"])
			else:
				max_req_bw_ul = None

			if "max_req_bw_dl" in self.request["subscription"]:
				max_req_bw_dl = int(self.request["subscription"]["max_req_bw_dl"])
			else:
				max_req_bw_dl = None

			self.profile = {
								"subscriber": {
												"imsi": int(self.request["identities"]["imsi"]),
												"key": bytes.fromhex(self.request["auth"]["key"]),
												"opc": bytes.fromhex(self.request["auth"]["opc"]),
												"amf": bytes.fromhex(self.request["auth"]["amf"]),
												"sqn": bytes.fromhex(self.request["auth"]["sqn"]),
												"msisdn": int(self.request["identities"]["msisdn"]),
												"schar": self.request["subscription"]["schar"],
												"stn_sr": stn_sr,
												"odb": odb,
												"roaming_allowed": roaming_allowed,
												"max_req_bw_ul": max_req_bw_ul,
												"max_req_bw_dl": max_req_bw_dl,
												"default_apn": self.request["subscription"]["default_apn"],
								},
								"apns": self.request["subscription"]["apns"]
			}
			return True
		return False


class ApnParser(Parser):
	def __init__(self, request):
		super().__init__(request, "apn-request")


class Response:
    @staticmethod
    def resource_found(resource):
        return make_response(
            jsonify(resource), 
            HTTP_200_OK
        )

    @staticmethod
    def resource_created():
        return make_response(
            {}, 
            HTTP_201_CREATED
        )

    @staticmethod
    def no_content():
        return make_response(
            {}, 
            HTTP_204_NO_CONTENT
        )

    @staticmethod
    def invalid_json_format():
        return make_response(
            jsonify({"error_message": "Invalid JSON format"}), 
            HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def invalid_data_content():
        return make_response(
            jsonify({"error_message": "Invalid data content"}), 
            HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def invalid_url_param_format(error_message):
        return make_response(
            jsonify({"error_message": f"Invalid URL parameter format: {error_message}"}), 
            HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def invalid_json_schema(error_message):
        return make_response(
            jsonify({"error_message": error_message}), 
            HTTP_400_BAD_REQUEST
        )
		# "Invalid JSON schema"
    @staticmethod
    def resource_not_found():
        return make_response(
            {}, 
            HTTP_404_NOT_FOUND
        )

    @staticmethod
    def server_internal_error(error_message):
        return make_response(
            jsonify({"error_message": error_message}), 
            HTTP_500_SERVER_INTERNAL_ERROR
        )