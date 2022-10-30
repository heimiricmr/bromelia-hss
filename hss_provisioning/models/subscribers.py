# -*- coding: utf-8 -*-
"""
    hss_provisioning.models.subscribers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module contains functions to handle Subscribers model in 
    Bromelia-HSS's database.

    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

from . import (
    Apn,
    Mip6,
    Session,
    Subscriber, 
)
from exceptions import UnknownSubscriber


def norm(subscriber):
    content = {
        "subscriber_id": subscriber["id"],
        "identities": {
            "imsi": str(subscriber["imsi"]),
            "msisdn": str(subscriber["msisdn"])
        },
        "auth": {
            "key": subscriber["key"],
            "opc": subscriber["opc"],
            "amf": subscriber["amf"],
            "sqn": subscriber["sqn"]
        },
        "subscription": {
            "schar": subscriber["schar"],
            "default_apn": subscriber["default_apn"],
            "apns": subscriber["apns"],
            "roaming_allowed": subscriber["roaming_allowed"]
        }
    }

    if subscriber["stn_sr"]:
        content["subscription"]["stn_sr"] = str(subscriber["stn_sr"])

    if subscriber["odb"]:
        content["subscription"]["odb"] = subscriber["odb"]

    if subscriber["max_req_bw_ul"]:
        content["subscription"]["max_req_bw_ul"] = subscriber["max_req_bw_ul"]

    if subscriber["max_req_bw_dl"]:
        content["subscription"]["max_req_bw_dl"] = subscriber["max_req_bw_dl"]

    content.update({
            "service": {
                "ue_srvcc_support": subscriber["ue_srvcc_support"],
                "mme_hostname": subscriber["mme_hostname"],
                "mme_realm": subscriber["mme_realm"],
                "mip6s": subscriber["mip6s"],
            }})
    return content


class EpsSubscriber():
    def __init__(self, profile):
        self.profile = profile

    @property
    def subscriber(self):
        return Subscriber(**self.profile["subscriber"])

    @property
    def imsi(self):
        try:
            return self.profile["subscriber"]["imsi"]
        except:
            return None

    @property
    def msisdn(self):
        try:
            return self.profile["subscriber"]["msisdn"]
        except:
            return None

    @property
    def default_apn(self):
        return self.profile["subscriber"]["default_apn"]

    @property
    def apns(self):
        return self.profile["apns"]

    def imsi_already_exists(self):
        subscriber = get_subscriber_by_imsi(self.imsi)
        if subscriber is not None:
            self.subscriber_mismatch = subscriber.msisdn
            return True
        return False

    def msisdn_already_exists(self):
        subscriber = get_subscriber_by_msisdn(self.msisdn)
        if subscriber is not None:
            self.subscriber_mismatch = subscriber.msisdn
            return True
        return False


def get_subscriber_by_imsi(imsi):
    if imsi is not None:
        with Session.begin() as session:
            return session.query(
                    Subscriber
                ).filter(
                    Subscriber.imsi==imsi
                ).one_or_none()


def get_subscriber_by_msisdn(msisdn):
    if msisdn is not None:
        with Session.begin() as session:
            return session.query(
                    Subscriber
                ).filter(
                    Subscriber.msisdn==msisdn
                ).one_or_none()


def create_eps_subscriber(subscriber):
    eps_subscriber = EpsSubscriber(subscriber)

    if eps_subscriber.imsi_already_exists():
        raise Exception(f"Subscriber already defined for IMSI - "\
                        f"(MSISDN: {eps_subscriber.subscriber_mismatch})")

    if eps_subscriber.msisdn_already_exists():
        raise Exception(f"Subscriber already defined for MSISDN - "\
                        f"(IMSI: {eps_subscriber.subscriber_mismatch})")


    if not eps_subscriber.default_apn in eps_subscriber.apns:
        raise Exception(f"Default APN must be provided in 'apns' property")

    subscriber = eps_subscriber.subscriber

    with Session.begin() as session:
        for apn_id in eps_subscriber.apns:
            apn = session.query(
                    Apn
                ).filter(
                    Apn.apn_id==apn_id
                ).one_or_none()

            if apn is None:
                raise Exception(f"Unknown APN id: {apn_id}")

            subscriber.apns.append(apn)
            subscriber.mip6s.append(Mip6(context_id=apn_id))

            session.add(subscriber)


def get_eps_subscriber(subscriber_id):
    with Session.begin() as session:
        subscriber = session.query(
                Subscriber
            ).filter(
                Subscriber.id==subscriber_id
            ).one_or_none()

    if subscriber is not None:
        return norm(subscriber.as_dict(relationship=True))


def get_eps_subscriber_by_imsi(imsi):
    with Session.begin() as session:
        subscriber = session.query(
                Subscriber
            ).filter(
                Subscriber.imsi==imsi
            ).one_or_none()

    if subscriber is not None:
        return norm(subscriber.as_dict(relationship=True))


def get_eps_subscriber_by_msisdn(msisdn):
    with Session.begin() as session:
        subscriber = session.query(
                Subscriber
            ).filter(
                Subscriber.msisdn==msisdn
            ).one_or_none()

    if subscriber is not None:
        return norm(subscriber.as_dict(relationship=True))


def get_eps_subscribers():
    with Session.begin() as session:
        subscribers = session.query(Subscriber).all()

    return [ norm(subscriber.as_dict(relationship=True)) for subscriber in subscribers ]


def delete_eps_subscriber_by_imsi(imsi):
    with Session.begin() as session:
        subscriber = session.query(
                Subscriber
            ).filter(
                Subscriber.imsi==imsi
            ).one_or_none()

        if subscriber is None:
            raise UnknownSubscriber("Unknown subscriber")
        
        session.delete(subscriber)


def delete_eps_subscriber_by_msisdn(msisdn):
    with Session.begin() as session:
        subscriber = session.query(
                Subscriber
            ).filter(
                Subscriber.msisdn==msisdn
            ).one_or_none()

        if subscriber is None:
            raise UnknownSubscriber("Unknown subscriber")
        
        session.delete(subscriber)