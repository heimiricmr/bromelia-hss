# -*- coding: utf-8 -*-
"""
    bromelia_hss.tests.s6a_mme_bromelia
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module contains an example on how to setup a dummy MME by using the
    Bromelia class features of bromelia library.
    
    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

#: Python standard libs
import json
import os
import random
import requests
import time
import sys

#: 3rd-party dependencies
from bromelia import Bromelia
from bromelia.avps import *
from bromelia.constants import *
from bromelia.lib.etsi_3gpp_s6a.avps import *
from bromelia.lib.etsi_3gpp_s6a.messages import AuthenticationInformationAnswer as AIA
from bromelia.lib.etsi_3gpp_s6a.messages import AuthenticationInformationRequest as AIR
from bromelia.lib.etsi_3gpp_s6a.messages import CancelLocationAnswer as CLA
from bromelia.lib.etsi_3gpp_s6a.messages import CancelLocationRequest as CLR
from bromelia.lib.etsi_3gpp_s6a.messages import NotifyAnswer as NOA
from bromelia.lib.etsi_3gpp_s6a.messages import NotifyRequest as NOR
from bromelia.lib.etsi_3gpp_s6a.messages import PurgeUeAnswer as PUA
from bromelia.lib.etsi_3gpp_s6a.messages import PurgeUeRequest as PUR
from bromelia.lib.etsi_3gpp_s6a.messages import UpdateLocationAnswer as ULA
from bromelia.lib.etsi_3gpp_s6a.messages import UpdateLocationRequest as ULR

#: project modules
from messages import Air, Nor, Pur, Ulr

local_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(local_dir, "s6a_mme_bromelia.yaml")

#: Application initialization
msgs = [AIA, AIR, CLA, CLR, NOA, NOR, PUA, PUR, ULA, ULR]

app = Bromelia(config_file=config_file)
app.load_messages_into_application_id(msgs, DIAMETER_APPLICATION_S6a_S6d)


@app.route(application_id=DIAMETER_APPLICATION_S6a_S6d, command_code=CANCEL_LOCATION_MESSAGE)
def clr(request):
    return app.s6a.CLA()


@app.route(application_id=DIAMETER_APPLICATION_S6a_S6d, command_code=PURGE_UE_MESSAGE)
def pur(request):
    return app.s6a.PUA(pua_flags=0x00000001)


#: Dict with Diameter Base AVPs
base_avps = {
        "session_id": app.configs[0]["LOCAL_NODE_HOSTNAME"],
        "origin_host": app.configs[0]["LOCAL_NODE_HOSTNAME"],
        "origin_realm": app.configs[0]["LOCAL_NODE_REALM"],
        "destination_realm": app.configs[0]["PEER_NODE_REALM"],
        "destination_host": app.configs[0]["PEER_NODE_HOSTNAME"],    
}

#: Setup variables to APN creation
base_url_apn = "http://localhost:5001/apns"

#: Setup variables to subscriber creation
base_url_subscriber = "http://localhost:5001/subscribers"


def setup():
    #: Create APN internet
    content = {
        "apn_id": 1,
        "apn_name": "internet",
        "pdn_type": "IPv4",
        "qci": 9,
        "priority_level": 8,
        "max_req_bw_ul": 999999999,
        "max_req_bw_dl": 999999999
    }

    r = requests.post(
        base_url_apn, 
        data=json.dumps(content), 
        headers={"Content-Type": "application/json"}
    )

    #: Create APN mms
    content = {
        "apn_id": 3,
        "apn_name": "mms",
        "pdn_type": "IPv4",
        "qci": 9,
        "priority_level": 8,
        "max_req_bw_ul": 256,
        "max_req_bw_dl": 256
    }

    r = requests.post(
        base_url_apn, 
        data=json.dumps(content), 
        headers={"Content-Type": "application/json"}
    )

    #: Create APN internetlte
    content = {
        "apn_id": 4,
        "apn_name": "internetlte",
        "pdn_type": "IPv4v6",
        "qci": 9,
        "priority_level": 8,
        "max_req_bw_ul": 999999999,
        "max_req_bw_dl": 999999999
    }

    r = requests.post(
        base_url_apn, 
        data=json.dumps(content), 
        headers={"Content-Type": "application/json"}
    )

    #: Create APN ims
    content = {
        "apn_id": 824,
        "apn_name": "ims",
        "pdn_type": "IPv4v6",
        "qci": 5,
        "priority_level": 8,
        "max_req_bw_ul": 256,
        "max_req_bw_dl": 256
    }

    r = requests.post(
        base_url_apn, 
        data=json.dumps(content), 
        headers={"Content-Type": "application/json"}
    )

    content = {
        "identities": {
            "imsi": "999000000000001",
            "msisdn": "5521000000001"
        },
        "auth": {
            "key": "465b5ce8b199b49faa5f0a2ee238a6bc",
            "opc": "013d7d16d7ad4fefb61bd95b765c8ceb",
            "amf": "b9b9",
            "sqn": "ff9bb4d0b607"
        },
        "subscription": {
            "schar": 8,
            "stn_sr": "5500599999999",
            "roaming_allowed": False,
            "max_req_bw_ul": 100000,
            "max_req_bw_dl": 100000,
            "default_apn": 1,
            "apns": [
                1,
                3,
                4,
                824
            ]
        }
    }

    #: Create Subscriber #1
    r = requests.post(
        base_url_subscriber, 
        data=json.dumps(content), 
        headers={"Content-Type": "application/json"}
    )

    #: Create Subscriber #2
    subscriber_with_odb_all_apn = "999000000000002"
    content["identities"]["imsi"] = subscriber_with_odb_all_apn
    content["identities"]["msisdn"] = "5521000000002"
    content["subscription"]["odb"] = "ODB-all-APN"

    r = requests.post(
        base_url_subscriber, 
        data=json.dumps(content), 
        headers={"Content-Type": "application/json"}
    )

    #: Create Subscriber #3
    subscriber_with_odb_hplmn_apn = "999000000000003"
    content["identities"]["imsi"] = subscriber_with_odb_hplmn_apn
    content["identities"]["msisdn"] = "5521000000003"
    content["subscription"]["odb"] = "ODB-HPLMN-APN"

    r = requests.post(
        base_url_subscriber, 
        data=json.dumps(content), 
        headers={"Content-Type": "application/json"}
    )

    #: Create Subscriber #4
    subscriber_with_odb_vplmn_apn = "999000000000004"
    content["identities"]["imsi"] = subscriber_with_odb_vplmn_apn
    content["identities"]["msisdn"] = "5521000000004"
    content["subscription"]["odb"] = "ODB-VPLMN-APN"

    r = requests.post(
        base_url_subscriber, 
        data=json.dumps(content), 
        headers={"Content-Type": "application/json"}
    )


def tear_down():
    #: Delete Subscribers
    r = requests.delete(f"{base_url_subscriber}/imsi/999000000000001")
    r = requests.delete(f"{base_url_subscriber}/imsi/999000000000002")
    r = requests.delete(f"{base_url_subscriber}/imsi/999000000000003")
    r = requests.delete(f"{base_url_subscriber}/imsi/999000000000004")

    #: Delete APN
    r = requests.delete(f"{base_url_apn}/1")
    r = requests.delete(f"{base_url_apn}/3")
    r = requests.delete(f"{base_url_apn}/4")
    r = requests.delete(f"{base_url_apn}/824")


def create_air(index):
    imsi = str(999000000000000 + index)

    air_avps = {"user_name": imsi}
    return Air.create(**{**base_avps, **air_avps})


def create_nor(index):
    imsi = str(999000000000000 + index)

    nor_avps = {"user_name": imsi}
    return Nor.create(**{**base_avps, **nor_avps})


def create_pur(index):
    imsi = str(999000000000000 + index)

    pur_avps = {
                "user_name": imsi,
                "vendor_specific_application_id": [
                    VendorIdAVP(VENDOR_ID_3GPP), 
                    AuthApplicationIdAVP(DIAMETER_APPLICATION_S6a_S6d)
                ],
    }
    return Pur.create(**{**base_avps, **pur_avps})


def create_ulr(index):
    imsi = str(999000000000000 + index)
    imei = str(123456789000000 + index)

    ulr_avps = {
        "user_name": imsi,
        "terminal_information": [
            ImeiAVP(imei),
            SoftwareVersionAVP("12")
        ],
    }
    return Ulr.create(**{**base_avps, **ulr_avps})


def functional_test(app, func):
    msg = func(1)

    answer = app.send_message(msg)
    print(f"-->> msg: {msg}\n-->> answer: {answer}")


def performance_test(app, func):
    msgs = list()
    total_recvd = 0

    num_msgs = 2000
    start = datetime.datetime.utcnow()

    for index in range(1, num_msgs + 1):
        msg = func(index)
        msgs.append(msg)

        if index % 50 == 0:
            print(f"index: {index}, msgs: {len(msgs)}, total_recv: {total_recvd}, %: {100*round(total_recvd/index,2)}")
            app.send_messages(msgs)
            msgs = list()

            time.sleep(1)

            total_recvd = app._association.num_answers
            # print(app._association.pending_requests)
    
    print(f"index: {num_msgs+1}, msgs: {len(msgs)}, total_recv: {total_recvd}, %: {100*round(total_recvd/(num_msgs+1),2)}")
    app.send_messages(msgs)
    msgs = list()

    while total_recvd < num_msgs:
        total_recvd = app._association.num_answers

    stop = datetime.datetime.utcnow()


    executed_time = (stop - start).seconds
    try:
        tps = round(num_msgs/executed_time,3)
    except ZeroDivisionError:
        tps = None

    print(f"\n\nexecuted time: {executed_time} seconds")
    print(f"tps: {tps} msgs/seconds")


subscribers = [
    "999000000000001", 
    "999000000000002", 
    "999000000000003", 
    "999000000000004"
]

func_params = {
    "with_immediate_response_preferred_avp": random.randint(1,3),
    "without_immediate_response_preferred_avp": random.randint(1,3),
    "too_much_immediate_response_preferred": random.randint(1,3),
    "too_much_number_of_requested_vectors": random.randint(1,3),
    "roaming_not_allowed": random.choice(subscribers),
    "regular_with_odb": random.choice(subscribers),
    "realm_not_served": random.choice(subscribers),
}

message_options = {
    "1": create_air,
    "2": create_nor,
    "3": create_pur,
    "4": create_ulr
}

FUNCTIONAL_TESTS = "1"
PERFORMANCE_TESTS = "2"
PERFORMANCE_WITH_VARIANT_TESTS = "3"


def load_funcs():
    airs = Air.get_staticmethods()
    nors = Nor.get_staticmethods()
    purs = Pur.get_staticmethods()
    ulrs = Ulr.get_staticmethods()

    return airs + nors + purs + ulrs


def _random():
    _sum = {"air": 0, "nor": 0, "pur": 0, "ulr": 0}
    funcs = load_funcs()

    _total = 0
    for index in range(100):
        class_name, func_name, _func = random.choice(funcs)
        func = _func.__func__
        if func_name in func_params:
            param = func_params[func_name]
            print(f"{index}, params, {class_name}, {func_name}, {func}, {param}")
            msg = func(param, **base_avps)
        else:
            print(f"{index}, no-params, {class_name}, {func_name}, {func}")
            msg = func(**base_avps)

        answer = app.send_message(msg)

        _total += 1

        if class_name == "air":
            _sum["air"] += 1
        elif class_name == "nor":
            _sum["nor"] += 1
        elif class_name == "pur":
            _sum["pur"] += 1
        elif class_name == "ulr":
            _sum["ulr"] += 1

    print(_sum, _total)


def performance_with_diff_test():
    setup()
    _random()
    tear_down()


def exec_testing_option():
    while 1:
        option = str(input(">> Choose a testing option: (1) Functional (2) Performance (3) Performance with diff messages (4) Exit "))

        if option not in ["1", "2", "3", "4"]:
            print("You need to choose one of the testing options above")
        else:
            if option == "4":
                sys.exit()
            return option


def exec_message_option():
    while 1:
        option = str(input(">> Choose a Message to be sent: (1) AIR, (2) NOR, (3) PUR, (4) ULR, (5) Exit "))

        if option not in ["1", "2", "3", "4", "5"]:
            print("You need to choose one of the message options above")
            sys.exit(0)
        else:
            if option == "5":
                sys.exit()
            return option


def testing_app(app):
    try:
        print(f"\n===================================================\n")

        testing_option = exec_testing_option()

        if testing_option == FUNCTIONAL_TESTS:
            functional_test(app, message_options[exec_message_option()])

        elif testing_option == PERFORMANCE_TESTS:
            _app = app.associations[b'\x01\x00\x00#'].app
            performance_test(_app, message_options[exec_message_option()])

        elif testing_option == PERFORMANCE_WITH_VARIANT_TESTS:
            performance_with_diff_test()

        print(f"\n===================================================\n")
    except:
        sys.exit(0)


def main():
    app.run()

    while 1:
        testing_app(app)

        _continue = input("\n>> Continue with more tests? (Y/N) ")
        if not (_continue == "Y" or _continue == "y"):
            break


if __name__ == "__main__":
    main()
