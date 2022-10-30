# -*- coding: utf-8 -*-
"""
    hss_provisioning.models
    ~~~~~~~~~~~~~~~~~~~~~~~

    This module contains Bromelia-HSS database's data models.

    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

from copy import deepcopy

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    backref, 
    relationship, 
    sessionmaker
)

from config import *


engine = create_engine(SQL_BASE_URI, echo=True)
Session = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


def norm(value):
    if isinstance(value, bytes):
        return value.hex()
    return value


class HssBaseModel:
    def as_dict(self, relationship=False):
        if not relationship:
            return {c.name: norm(getattr(self, c.name)) for c in self.__table__.columns}

        d = deepcopy(self.__dict__)
        d.pop("_sa_instance_state")

        for key, value in d.items():
            if isinstance(value, list):
                d[key] = [ v.as_dict() for v in value ]

            elif isinstance(value, bytes):
                d[key] = value.hex()

        return d


#: https://medium.com/@ns2586/sqlalchemys-relationship-and-lazy-parameter-4a553257d9ef
class Subscriber(Base, HssBaseModel):
    __tablename__ = "subscribers"
    id = Column(BigInteger, primary_key=True)

    imsi = Column(BigInteger)
    key = Column(LargeBinary)
    opc = Column(LargeBinary)
    amf = Column(LargeBinary)
    sqn = Column(LargeBinary)

    msisdn = Column(BigInteger)
    stn_sr = Column(BigInteger)
    roaming_allowed = Column(Boolean)
    odb = Column(String)
    schar = Column(Integer)
    max_req_bw_ul = Column(BigInteger)
    max_req_bw_dl = Column(BigInteger)
    default_apn = Column(Integer)

    mme_hostname = Column(String)
    mme_realm = Column(String)
    ue_srvcc_support = Column(Boolean)

    apns = relationship("Apn", secondary="subscriber_apns", lazy="joined", overlaps="apns,subscribers")
    mip6s = relationship("Mip6", secondary="subscriber_mip6s", lazy="joined", overlaps="mip6s,subscribers")


class Apn(Base, HssBaseModel):
    __tablename__ = "apns"
    id = Column(BigInteger, primary_key=True)

    apn_id = Column(Integer)
    apn_name = Column(String)
    pdn_type = Column(String)
    qci = Column(Integer)
    priority_level = Column(Integer)
    max_req_bw_ul = Column(BigInteger)
    max_req_bw_dl = Column(BigInteger)

    subscribers = relationship("Subscriber", secondary="subscriber_apns", lazy="joined", overlaps="apns")


class Mip6(Base, HssBaseModel):
    __tablename__ = "mip6s"
    id = Column(BigInteger, primary_key=True)

    context_id = Column(Integer)
    service_selection = Column(String)
    destination_realm = Column(String)
    destination_host = Column(String)

    subscribers = relationship("Subscriber", secondary="subscriber_mip6s", lazy="joined", overlaps="mip6")


class SubscriberApns(Base, HssBaseModel):
    __tablename__ = "subscriber_apns"
    id = Column(BigInteger, primary_key=True)
    subscriber_id = Column(BigInteger, ForeignKey("subscribers.id"))
    apn_id = Column(BigInteger, ForeignKey("apns.id"))

    subscriber = relationship(Subscriber, backref=backref("subscriber_apns", cascade="all, delete-orphan"), overlaps="mip6s,subscribers")
    apn = relationship(Apn, backref=backref("subscriber_apns", cascade="all, delete-orphan"), overlaps="apns")


class SubscriberMip6s(Base, HssBaseModel):
    __tablename__ = "subscriber_mip6s"
    id = Column(BigInteger, primary_key=True)
    subscriber_id = Column(BigInteger, ForeignKey("subscribers.id"))
    mip6_id = Column(BigInteger, ForeignKey("mip6s.id"))

    subscriber = relationship(Subscriber, backref=backref("subscriber_mip6s", cascade="all, delete-orphan"), overlaps="mip6s,subscribers")
    mip6 = relationship(Mip6, backref=backref("subscriber_mip6s", cascade="all, delete-orphan"), overlaps="mip6s")


Base.metadata.create_all(engine)
