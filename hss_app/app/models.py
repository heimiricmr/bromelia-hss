# -*- coding: utf-8 -*-
"""
    hss_app.models
    ~~~~~~~~~~~~~~

    This module contains HSS's database models.
    
    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

from config import Config

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import BigInteger, Column, Integer, LargeBinary, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker

engine = create_engine(Config.SQL_BASE_URI, echo=True)
Session = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()


class Subscriber(Base):
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

    apns = relationship("Apn", lazy="joined", secondary="subscriber_apns", 
                        order_by="Apn.apn_id")
    mip6s = relationship("Mip6", lazy="joined", secondary="subscriber_mip6s", 
                         order_by="Mip6.context_id")


class Apn(Base):
    __tablename__ = "apns"
    id = Column(BigInteger, primary_key=True)

    apn_id = Column(Integer)
    apn_name = Column(String)
    pdn_type = Column(String)
    qci = Column(Integer)
    priority_level = Column(Integer)
    max_req_bw_ul = Column(BigInteger)
    max_req_bw_dl = Column(BigInteger)

    subscribers = relationship("Subscriber", secondary="subscriber_apns")


class Mip6(Base):
    __tablename__ = "mip6s"
    id = Column(BigInteger, primary_key=True)

    context_id = Column(Integer)
    service_selection = Column(String)
    destination_realm = Column(String)
    destination_host = Column(String)

    subscribers = relationship("Subscriber", secondary="subscriber_mip6s")


class SubscriberApns(Base):
    __tablename__ = "subscriber_apns"
    id = Column(BigInteger, primary_key=True)
    subscriber_id = Column(BigInteger, ForeignKey("subscribers.id"))
    apn_id = Column(BigInteger, ForeignKey("apns.id"))

    subscriber = relationship(Subscriber, 
                              backref=backref("subscriber_apns", 
                                              cascade="all, delete-orphan"))
    apn = relationship(Apn, 
                       backref=backref("subscriber_apns", 
                                       cascade="all, delete-orphan"))


class SubscriberMip6s(Base):
    __tablename__ = "subscriber_mip6s"
    id = Column(BigInteger, primary_key=True)
    subscriber_id = Column(BigInteger, ForeignKey("subscribers.id"))
    mip6_id = Column(BigInteger, ForeignKey("mip6s.id"))

    subscriber = relationship(Subscriber, 
                              backref=backref("subscriber_mip6s", 
                                              cascade="all, delete-orphan"))

    mip6 = relationship(Mip6, 
                        backref=backref("subscriber_mip6s", 
                                        cascade="all, delete-orphan"))


Base.metadata.create_all(engine)


def get_eps_subscription_profile(imsi: str) -> Subscriber:
    with Session.begin() as session:
        return session.query(
                                Subscriber
                            ).filter(
                                Subscriber.imsi==imsi
                            ).one_or_none()


def update_mip6_agent_info_eps_subscription_profile(imsi: str, profile: dict) -> None:
    with Session.begin() as session:
        subscriber = session.query(
                                Subscriber
                            ).filter(
                                Subscriber.imsi==imsi
                            ).one_or_none()

        mip6 = list(filter(lambda mip6: mip6.context_id == profile["context_id"], subscriber.mip6s))

        if mip6:
            setattr(mip6[0], "destination_host", profile["destination_host"])
            setattr(mip6[0], "destination_realm", profile["destination_realm"])


def update_mme_info_eps_subscription_profile(imsi: str, profile: dict) -> None:
    with Session.begin() as session:
        subscriber = session.query(
                                Subscriber,
                            ).filter(
                                Subscriber.imsi==imsi
                            ).one_or_none()

        if subscriber is not None:
            setattr(subscriber, "mme_hostname", profile["mme_hostname"])
            setattr(subscriber, "mme_realm", profile["mme_realm"])
            setattr(subscriber, "ue_srvcc_support", profile["ue_srvcc_support"])


def update_sqn_info_eps_subscription_profile(imsi: str, profile: dict) -> None:
    with Session.begin() as session:
        subscriber = session.query(
                                Subscriber,
                            ).filter(
                                Subscriber.imsi==imsi
                            ).one_or_none()

        if subscriber is not None:
            setattr(subscriber, "sqn", profile["sqn"])