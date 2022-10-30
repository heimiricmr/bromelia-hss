# -*- coding: utf-8 -*-
"""
    hss_provisioning.constants
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module defines Bromelia-HSS Provisioning app's constants.

    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

#: Init variables to use as HTTP status code. For more info regarding others
#: status code, please refer to the HTTP RFC 7231 spec.

#: HTTP 2xx success
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

#: HTTP 4xx client errors
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404

#: HTTP 5xx server errors
HTTP_500_SERVER_INTERNAL_ERROR = 500

#: Initializing variables to use as HSS API status code when HTTP 5xx family
#: has raised. For more info regarding others status codes, please refer to
#: api_status_code.json file.
HSS_API_INVALID_DATA_CONTENT = 7400
HSS_API_INVALID_JSON_TEXT = 7401
HSS_API_INVALID_JSON_SCHEMA = 7402
HSS_API_INTERNAL_SERVER_ERROR = 7403