# -*- coding: utf-8 -*-
"""
    hss_provisioning.routes.apns
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module contains APN resource's routes endpoints.

    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

import json

import sqlalchemy
from flask import (
    Blueprint,
    request
)

from models.apns import (
    create_apn, 
    delete_apn, 
    get_apns,
    get_apn_by_id,
)
from utils import (
    ApnParser,
    Response,
    get_json_content,
)


bp = Blueprint("apns", __name__)


@bp.route("/apns", methods=["POST"])
def api_create_apn():
    #: Verify if incoming request is well formatted
    try:
        json_content = get_json_content(request)

    except json.decoder.JSONDecodeError:
        return Response.invalid_json_format()

    except Exception:
        return Response.invalid_data_content()

    #: Verify if incoming request data content complies to JSON API Schema.
    api_request = ApnParser(json_content)

    if not api_request.is_valid():
        return Response.invalid_json_schema(error_message=api_request.get_error_message())

    #: Create APN
    try:
        create_apn(api_request.request)
        return Response.resource_created()

    except Exception as e:
        return Response.server_internal_error(error_message=e.args[0])


@bp.route("/apns/<apn_id>", methods=["GET"])
def api_get_apn_by_id(apn_id):
    try:
        apn = get_apn_by_id(apn_id)
        return Response.resource_found(apn)

    except Exception as e:
        return Response.server_internal_error(error_message=e.args[0])


@bp.route("/apns", methods=["GET"])
def api_get_apns():
    try:
        apns = get_apns()
        return Response.resource_found(apns)

    except Exception as e:
        return Response.server_internal_error(error_message=e.args[0])


@bp.route("/apns/<apn_id>", methods=["DELETE"])
def api_delete_apn(apn_id):
    try:
        delete_apn(apn_id)
        return Response.no_content()

    except sqlalchemy.exc.IntegrityError:
        error_message = "Cannot delete an APN in use"
        return Response.server_internal_error(error_message=error_message)
    
    except Exception as e:
        return Response.server_internal_error(error_message=e.args[0])
