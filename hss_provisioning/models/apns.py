# -*- coding: utf-8 -*-
"""
    hss_provisioning.models.apns
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module contains functions to handle APN model in 
    Bromelia-HSS's database.

    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

from . import (
    Apn,
    Session
)


def create_apn(apn):
    with Session.begin() as session:
        _apn = session.query(Apn).filter(Apn.apn_id==apn["apn_id"]).one_or_none()

        if _apn is not None:
            raise Exception(f"APN Id already defined: {apn['apn_id']}")

        session.add(Apn(**apn))


def get_apn_by_id(apn_id):
    with Session.begin() as session:
        _apn = session.query(Apn).filter(Apn.apn_id==apn_id).one_or_none()

        if _apn is None:
            raise Exception(f"APN Id not defined: {apn_id}")

        return _apn.as_dict()


def get_apns():
    with Session.begin() as session:
        apns = session.query(Apn).all()
    
    return [ apn.as_dict() for apn in apns ]


def delete_apn(apn_id):
    with Session.begin() as session:
        session.query(Apn).filter(Apn.apn_id==apn_id).delete()
