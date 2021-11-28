# -*- coding: utf-8 -*-
"""
    hss_app.entrypoint
    ~~~~~~~~~~~~~~~~~~

    The central entrypoint to run HSS network function.

    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

from app import app

if __name__ == "__main__":
    app.run(debug=True, is_logging=True)   #: It will be blocked until connection has been established