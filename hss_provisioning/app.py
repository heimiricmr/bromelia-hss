# -*- coding: utf-8 -*-
"""
    hss_provisioning.app
    ~~~~~~~~~~~~~~~~~~~~

    This module implements Bromelia-HSS Provisioning app's initialization.

    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from config import *
from routes import *

session = Session()
db = SQLAlchemy()


def setup_routes(app):
	app.register_blueprint(bp_subscribers)
	app.register_blueprint(bp_apns)


def create_app():
	app = Flask(__name__)
	app.config.update(
		SECRET_KEY=SECRET_KEY,
		SQLALCHEMY_BINDS=SQLALCHEMY_BINDS,
	)

	setup_routes(app)

	with app.app_context():
		session.init_app(app)
		db.init_app(app)
	
	return app

app = create_app()

import routes