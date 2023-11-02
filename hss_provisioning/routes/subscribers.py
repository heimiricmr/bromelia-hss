# -*- coding: utf-8 -*-
"""
    hss_provisioning.routes.subscribers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module contains Subscribers resource's routes endpoints.

    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

import json
import sys

from flask import (
    Blueprint,
    request
)

from exceptions import UnknownSubscriber
from models.subscribers import (
    create_eps_subscriber, 
    delete_eps_subscriber_by_imsi,
    delete_eps_subscriber_by_msisdn,
    get_eps_subscriber,
    get_eps_subscribers,
    get_eps_subscriber_by_imsi,
    get_eps_subscriber_by_msisdn,
)
from utils import (
    get_json_content,
    is_imsi,
    is_msisdn,
    Response,
    SubscriberParser
)


bp = Blueprint("subscribers", __name__)


def process_get_request(resource_func, resource_id=None):
    caller_func_name = sys._getframe().f_back.f_code.co_name

    if caller_func_name == "api_get_subscriber":
        if not resource_id.isdigit():
            return Response.invalid_url_param_format("it must be integer")
    
    elif caller_func_name == "api_get_subscriber_by_imsi":
        if not is_imsi(resource_id):
            return Response.invalid_url_param_format("it must be IMSI")

    elif caller_func_name == "api_get_subscriber_by_msisdn":
        if not is_msisdn(resource_id):
            return Response.invalid_url_param_format("it must be MSISDN")

    try:
        if resource_id is None:
            resource = resource_func()
        else:
            resource = resource_func(resource_id)

        if resource is not None:
            return Response.resource_found(resource=resource)
    
        return Response.resource_not_found()

    except Exception as e:
        return Response.server_internal_error(error_message=e.args[0])


def process_delete_request(resource_id, resource_func):
    try:
        resource_func(resource_id)
        return Response.no_content()

    except Exception as e:
        return Response.server_internal_error(error_message=e.args[0])


@bp.route("/subscribers", methods=["POST"])
def api_create_subscriber():
    #: Verify if incoming request is well formatted
    try:
        json_content = get_json_content(request)

    except json.decoder.JSONDecodeError:
        return Response.invalid_json_format()

    except Exception:
        return Response.invalid_data_content()

    #: Verify if incoming request data content complies to JSON API Schema.
    api_request = SubscriberParser(json_content)

    if not api_request.is_valid():
        return Response.invalid_json_schema(error_message=api_request.get_error_message())

    #: Create Subscriber
    try:
        create_eps_subscriber(api_request.profile)
        return Response.resource_created()

    except Exception as e:
        return Response.server_internal_error(error_message=e.args[0])


@bp.route("/subscribers/<subscriber_id>", methods=["GET"])
def api_get_subscriber(subscriber_id):
    return process_get_request(get_eps_subscriber, subscriber_id)


@bp.route("/subscribers/imsi/<imsi>", methods=["GET"])
def api_get_subscriber_by_imsi(imsi):
    return process_get_request(get_eps_subscriber_by_imsi, imsi)


@bp.route("/subscribers/msisdn/<msisdn>", methods=["GET"])
def api_get_subscriber_by_msisdn(msisdn):
    return process_get_request(get_eps_subscriber_by_msisdn, msisdn)


@bp.route("/subscribers", methods=["GET"])
def api_get_subscribers():
    return process_get_request(get_eps_subscribers)


@bp.route("/subscribers/imsi/<imsi>", methods=["DELETE"])
def api_delete_subscriber_by_imsi(imsi):
    try:
        return process_delete_request(imsi, delete_eps_subscriber_by_imsi)
    except UnknownSubscriber:
        return Response.resource_not_found()

@bp.route("/subscribers/msisdn/<msisdn>", methods=["DELETE"])
def api_delete_subscriber_by_msisdn(msisdn):
    try:
        return process_delete_request(msisdn, delete_eps_subscriber_by_msisdn)
    except UnknownSubscriber:
        return Response.resource_not_found()
