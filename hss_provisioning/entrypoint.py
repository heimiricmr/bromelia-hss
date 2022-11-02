# -*- coding: utf-8 -*-
"""
    hss_provisioning.entrypoint
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The central entrypoint to run Bromelia-HSS Provisioning app.

    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

from app import app
from config import Config

if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT)
