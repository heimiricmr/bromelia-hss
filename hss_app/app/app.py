# -*- coding: utf-8 -*-
"""
    hss_app.app
    ~~~~~~~~~~~

    This module implements HSS's core function.

    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

import logging

from bromelia import Bromelia
from bromelia.avps import *
from bromelia.lib.etsi_3gpp_s6a import AIA # AuthenticationInformationAnswer
from bromelia.lib.etsi_3gpp_s6a import AIR # AuthenticationInformationRequest
from bromelia.lib.etsi_3gpp_s6a import CLA # CancelLocationAnswer
from bromelia.lib.etsi_3gpp_s6a import CLR # CancelLocationRequest
from bromelia.lib.etsi_3gpp_s6a import NOA # NotifyAnswer
from bromelia.lib.etsi_3gpp_s6a import NOR # NotifyRequest
from bromelia.lib.etsi_3gpp_s6a import PUA # PurgeUeAnswer
from bromelia.lib.etsi_3gpp_s6a import PUR # PurgeUeRequest
from bromelia.lib.etsi_3gpp_s6a import ULA # UpdateLocationAnswer
from bromelia.lib.etsi_3gpp_s6a import ULR # UpdateLocationRequest
from bromelia.exceptions import *

from config import Config
from counters import app_counterdb
from models import (
    get_eps_subscription_profile,
    update_mip6_agent_info_eps_subscription_profile,
    update_mme_info_eps_subscription_profile,
    update_sqn_info_eps_subscription_profile
)
from utils import (
    create_subscription_data,
    create_supported_features,
    decode_from_plmn,
    generate_authentication_info_avp_data,
    generate_vectors,
    get_context_id,
    get_num_of_requested_vectors, 
    get_imsi, 
    get_immediate_response_preferred,
    get_mip6_agent_host_destination_host,
    get_mip6_agent_host_destination_realm,
    get_service_selection,
    get_visited_plmn,
    has_allowed_rat,
    is_new_mme_identity,
    is_subscriber_roaming,
    is_ue_srvcc_supported,
    ResponseGenerator
)

app_logger = logging.getLogger("3gpp_hss")

app = Bromelia(config_file=Config.config_file)

#: Application initialization
msgs = [AIA, AIR, CLA, CLR, NOA, NOR, PUA, PUR, ULA, ULR]
app.load_messages_into_application_id(msgs, DIAMETER_APPLICATION_S6a)


@app.route(application_id=DIAMETER_APPLICATION_S6a, command_code=AUTHENTICATION_INFORMATION_MESSAGE)
def air(request: AIR) -> AIA:
    """This function is the entrypoint to process S6a/S6d Diameter 
    Authentication-Information-Request messages.

    :param request: AuthenticationInformationRequest object

    :returns: AuthenticationInformationAnswer object
    """
    app_counterdb.incr("air:num_requests")

    hbh = request.header.hop_by_hop.hex()
    r = ResponseGenerator(request, proxy_response=app.s6a.AIA)

    try:
        imsi = get_imsi(request)
        app_logger.debug(f"[{hbh}] Got request from subscriber (IMSI: {imsi})")

    except DiameterMissingAvp as e:
        #: test__air_route__0__diameter_missing_user_name_avp
        app_counterdb.incr("air:num_answers:missing_avp")
        app_logger.exception(f"[{hbh}] Unable to get subscriber IMSI: {e.args[0]}")
        return r.missing_avp(msg=e.args[0])

    except DiameterInvalidAvpValue as e:
        #: test__air_route__1__diameter_invalid_user_name_avp_value
        app_counterdb.incr("air:num_answers:invalid_avp_value")
        app_logger.exception(f"[{hbh}] Unable to get subscriber IMSI: {e.args[0]}")
        return r.invalid_avp_value(msg=e.args[0], avp=request.user_name_avp)

    try:
        plmn = get_visited_plmn(request)
        mcc, mnc = decode_from_plmn(plmn)
        app_logger.debug(f"[{hbh}] Visited PLMN: (MCC: {mcc}, MNC: {mnc})")

    except DiameterMissingAvp as e:
        #: test__air_route__2__diameter_missing_visited_plmn_id_avp
        app_counterdb.incr("air:num_answers:missing_avp")
        app_logger.exception(f"[{hbh}] Unable to get visited PLMN: {e.args[0]}")
        return r.missing_avp(msg=e.args[0])


    try:
        num_of_requested_vectors = get_num_of_requested_vectors(request)
        app_logger.debug(f"[{hbh}] MME has requested this number of "\
                         f"vectors: {num_of_requested_vectors}")

    except DiameterMissingAvp as e:
        app_counterdb.incr("air:num_answers:missing_avp")
        app_logger.exception(f"[{hbh}] Unable to get the number of "\
                             f"requested vectors: {e.args[0]}")

        #: test__air_route__4__diameter_missing_requested_eutran_authentication_info_avp
        if e.args[0] == "Requested-EUTRAN-Authentication-Info AVP not found":
            return r.missing_avp(msg=e.args[0])

        #: test__air_route__5__diameter_missing_number_of_requested_vectors_avp
        if e.args[0] == "Number-Of-Requested-Vectors AVP not found":
            return r.missing_avp(msg=e.args[0], avp=request.requested_eutran_authentication_info_avp)


    subscriber = get_eps_subscription_profile(imsi)

    if subscriber is None:
        #: test__air_route__3__diameter_error_user_unknown
        app_counterdb.incr("air:num_answers:user_unknown")
        app_logger.debug(f"[{hbh}] Unknown subscriber: {imsi}")
        return r.user_unknown()

    key = subscriber.key
    app_logger.debug(f"[{hbh}] K: {key.hex()}")

    opc = subscriber.opc
    app_logger.debug(f"[{hbh}] OPc: {opc.hex()}")

    amf = subscriber.amf
    app_logger.debug(f"[{hbh}] AMF: {amf.hex()}")

    sqn = subscriber.sqn
    app_logger.debug(f"[{hbh}] SQN: {sqn.hex()}")

    res_preferred = get_immediate_response_preferred(request)
    app_logger.debug(f"[{hbh}] MME has requested this immediate response "\
                     f"preferred: {res_preferred}")

    if res_preferred is not None:
        num_of_vectors = res_preferred
        msg = "Too much vectors requested in Immediate-Response-Preferred AVP"
    else:
        num_of_vectors = num_of_requested_vectors
        msg = "Too much vectors requested in Number-Of-Requested-Vectors AVP"

    if num_of_vectors >= 5:
        #: test__air_route__9__diameter_authentication_data_unavailable__too_much_immediate_response_preferred
        #: test__air_route__10__diameter_authentication_data_unavailable__too_much_number_of_requested_vectors
        app_counterdb.incr("air:num_answers:authentication_data_unavailable")
        return r.authentication_data_unavailable(msg=msg, avp=request.requested_eutran_authentication_info_avp)

    # if is_resync_required(request):
    #     rand, auts = get_resync_data(request)
    #     sqn, _ = calculate_resync_data(key, opc, amf, rand, auts)

    vectors, sqn = generate_vectors(num_of_vectors, key, opc, amf, sqn, plmn)
    authentication_info_data = generate_authentication_info_avp_data(vectors)
    update_sqn_info_eps_subscription_profile(imsi, profile={"sqn": sqn})
    
    #: test__air_route__6__diameter_success__with_immediate_response_preferred_avp
    #: test__air_route__7__diameter_success__without_immediate_response_preferred_avp__number_of_requested_vectors_2
    #: test__air_route__8__diameter_success__without_immediate_response_preferred_avp__number_of_requested_vectors_3
    app_counterdb.incr("air:num_answers:success")
    return r.success(auth_session_state=NO_STATE_MAINTAINED, authentication_info=authentication_info_data)


@app.route(application_id=DIAMETER_APPLICATION_S6a, command_code=NOTIFY_MESSAGE)
def nor(request: NOR) -> NOA:
    """This function is the entrypoint to process S6a/S6d Diameter 
    Notify-Request messages.

    :param request: NotifyRequest object

    :returns: NotifyAnswer object
    """
    app_counterdb.incr("nor:num_requests")

    hbh = request.header.hop_by_hop.hex()
    r = ResponseGenerator(request, proxy_response=app.s6a.NA)

    #: When receiving a Notify request the HSS shall check whether the IMSI is 
    #: known.
    try:
        imsi = get_imsi(request)
        app_logger.debug(f"[{hbh}] Request from subscriber (IMSI: {imsi})")

    except DiameterMissingAvp as e:
        #: test__nor_route__0__diameter_missing_user_name_avp
        app_counterdb.incr("nor:num_answers:missing_avp")
        app_logger.exception(f"[{hbh}] Unable to get subscriber IMSI: {e.args[0]}")
        return r.missing_avp(msg=e.args[0])

    except DiameterInvalidAvpValue as e:
        #: test__nor_route__1__diameter_invalid_user_name_avp_value
        app_counterdb.incr("nor:num_answers:invalid_avp_value")
        app_logger.exception(f"[{hbh}] Unable to get subscriber IMSI: {e.args[0]}")
        return r.invalid_avp_value(msg=e.args[0], avp=request.user_name_avp)

    #: If it is not known, a result code of DIAMETER_ERROR_USER_UNKNOWN shall
    #: be returned. 
    subscriber = get_eps_subscription_profile(imsi)

    if subscriber is None:
        #: test__nor_route__2__diameter_error_user_unknown
        app_counterdb.incr("nor:num_answers:user_unknown")
        app_logger.debug(f"[{hbh}] Unknown subscriber: {imsi}")
        return r.user_unknown()

    #: If the IMSI is known, and the source MME or SGSN originating the Notify
    #: message is not currently registered in HSS for that UE, a result code of
    #: DIAMETER_ERROR_UNKNOWN_SERVING_NODE shall be returned.
    if is_new_mme_identity(request, subscriber):
        #: test__nor_route__3__diameter_error_unknown_serving_node
        app_counterdb.incr("nor:num_answers:unknown_serving_node")
        app_logger.debug(f"[{hbh}] Unknown serving node: "\
                         f"{request.origin_host_avp.data.decode('utf-8')}")
        return r.unknown_serving_node()

    try:
        profile = {
            "context_id": get_context_id(request),
            "service_selection": get_service_selection(request),
            "destination_host": get_mip6_agent_host_destination_host(request),
            "destination_realm": get_mip6_agent_host_destination_realm(request)
        }
        update_mip6_agent_info_eps_subscription_profile(imsi, profile)
        app_logger.exception(f"[{hbh}] Update dynamic profile info")

    except DiameterMissingAvp as e:
        app_counterdb.incr("nor:num_answers:missing_avp")
        app_logger.exception(f"[{hbh}] Unable to update MIP6-Agent-Info: {e.args[0]}")

        if e.args[0] == "MIP6-Agent-Info AVP not found":
            #: test__nor_route__5__diameter_missing_mip6_agent_info_avp
            return r.missing_avp(msg=e.args[0])

        if e.args[0] == "MIP-Home-Agent-Host AVP not found" or \
           e.args[0] == "Destination-Host AVP not found" or \
           e.args[0] == "Destination-Realm AVP not found":
            #: test__nor_route__6__diameter_missing_mip6_agent_info_avp__mip_home_agent_host
            #: test__nor_route__7__diameter_missing_mip6_agent_info_avp__destination_host
            #: test__nor_route__8__diameter_missing_mip6_agent_info_avp__destination_realm
            return r.missing_avp(msg=e.args[0], avp=request.mip6_agent_info_avp)

    #: test__nor_route__4__diameter_success
    app_counterdb.incr("nor:num_answers:success")
    return r.success()


@app.route(application_id=DIAMETER_APPLICATION_S6a, command_code=PURGE_UE_MESSAGE)
def pur(request: PUR) -> PUA:
    """This function is the entrypoint to process S6a/S6d Diameter 
    Purge-UE-Request messages.

    :param request: PurgeUeRequest object

    :returns: PurgeUeAnswer object
    """
    app_counterdb.incr("pur:num_requests")

    hbh = request.header.hop_by_hop.hex()
    r = ResponseGenerator(request, proxy_response=app.s6a.PUA)

    #: When receiving a Purge UE request the HSS shall check whether the IMSI 
    #: is known. 
    try:
        imsi = get_imsi(request)
        app_logger.debug(f"[{hbh}] Got request from subscriber (IMSI: {imsi})")

    except DiameterMissingAvp as e:
        #: test__pur_route__0__diameter_missing_user_name_avp
        app_counterdb.incr("pur:num_answers:missing_avp")
        app_logger.exception(f"[{hbh}] Unable to get subscriber IMSI: {e.args[0]}")
        return r.missing_avp(msg=e.args[0])

    except DiameterInvalidAvpValue as e:
        #: test__pur_route__1__diameter_invalid_user_name_avp_value
        app_counterdb.incr("pur:num_answers:invalid_avp_value")
        app_logger.exception(f"[{hbh}] Unable to get subscriber IMSI: {e.args[0]}")
        return r.invalid_avp_value(msg=e.args[0], avp=request.user_name_avp)


    #: If it is not known, a result code of DIAMETER_ERROR_USER_UNKNOWN shall 
    #: be returned.
    subscriber = get_eps_subscription_profile(imsi)

    if subscriber is None:
        #: test__pur_route__3__diameter_error_user_unknown
        app_counterdb.incr("pur:num_answers:user_unknown")
        app_logger.debug(f"[{hbh}] Unknown subscriber: {imsi}")
        return r.user_unknown()

    #: If it is known, the HSS shall set the result code to DIAMETER_SUCCESS 
    #: and compare the received identity in the Origin-Host with the stored
    #: MME-Identity and with the stored SGSN-Identity.
    if is_new_mme_identity(request, subscriber):
        app_logger.debug(f"[{hbh}] Received PUR message from a unknown "\
                         f"serving node: "\
                         f"{request.origin_host_avp.data.decode('utf-8')}")
        #: test__pur_route__5__diameter_success_with_new_mme
        app_counterdb.incr("pur:num_answers:success")
        return r.success(pua_flags=0x00000000)

    #: test__pur_route__4__diameter_success
    app_counterdb.incr("pur:num_answers:success")
    return r.success(pua_flags=0x00000001)


@app.route(application_id=DIAMETER_APPLICATION_S6a, command_code=UPDATE_LOCATION_MESSAGE)
def ulr(request: ULR) -> ULA:
    """This function is the entrypoint to process S6a/S6d Diameter 
    Update-Location-Request messages.

    :param request: UpdateLocationRequest object

    :returns: UpdateLocationAnswer object
    """
    app_counterdb.incr("ulr:num_requests")

    hbh = request.header.hop_by_hop.hex()
    r = ResponseGenerator(request, proxy_response=app.s6a.ULA)
    r.load_avps(supported_features=create_supported_features(), ula_flags=0x00000001)

    #: When receiving an Update Location request the HSS shall check whether
    #: subscription data exists for the IMSI
    try:
        imsi = get_imsi(request)
        app_logger.debug(f"[{hbh}] Got request from subscriber (IMSI: {imsi})")

    except DiameterMissingAvp as e:
        #: test__ulr_route__0__diameter_missing_user_name_avp
        app_counterdb.incr("ulr:num_answers:missing_avp")
        app_logger.exception(f"[{hbh}] Unable to get subscriber IMSI: {e.args[0]}")
        return r.missing_avp(msg=e.args[0])

    except DiameterInvalidAvpValue as e:
        #: test__ulr_route__1__diameter_invalid_user_name_avp_value
        app_counterdb.incr("ulr:num_answers:invalid_avp_value")
        app_logger.exception(f"[{hbh}] Unable to get subscriber IMSI: {e.args[0]}")
        return r.invalid_avp_value(avp=request.user_name_avp, msg=e.args[0])


    try:
        plmn = get_visited_plmn(request)
        mcc, mnc = decode_from_plmn(plmn)
        app_logger.debug(f"[{hbh}] Visited PLMN: (MCC: {mcc}, MNC: {mnc})")

    except DiameterMissingAvp as e:
        #: test__ulr_route__5__diameter_missing_visited_plmn_id_avp
        app_counterdb.incr("ulr:num_answers:missing_avp")
        app_logger.exception(f"[{hbh}] Unable to get visited PLMN: {e.args[0]}")
        return r.missing_avp(msg=e.args[0])


    #: The HSS shall check whether the RAT type the UE is using is allowed for
    #: the subscriber in the serving PLMN. If it is not, a Result Code of
    #: DIAMETER_ERROR_RAT_NOT_ALLOWED shall be returned. 
    if not has_allowed_rat(request):
        #: test__ulr_route__2__diameter_rat_not_allowed
        app_counterdb.incr("ulr:num_answers:rat_not_allowed")
        app_logger.debug(f"[{hbh}] Non-EUTRAN RAT type not allowed")
        return r.rat_not_allowed()


    subscriber = get_eps_subscription_profile(imsi)

    #: If the HSS determines that there is not any type of subscription for the
    #: IMSI (including EPS, GPRS and CS subscription data), a Result Code of
    #: DIAMETER_ERROR_USER_UNKNOWN shall be returned.
    if subscriber is None:
        #: test__ulr_route__3__diameter_error_user_unknown
        app_counterdb.incr("ulr:num_answers:user_unknown")
        app_logger.debug(f"[{hbh}] Unknown subscriber: {imsi}")
        return r.user_unknown()


    #: The HSS shall check whether roaming is not allowed in the VPLMN due to
    #: ODB. If so a Result Code of DIAMETER_ERROR_ROAMING_NOT_ALLOWED shall be
    #: returned. When this error is sent due to the MME or SGSN not supporting
    #: a certain ODB category, an Error Diagnostic information element may be
    #: added to indicate the type of ODB; if this error is sent due to the ODB
    #: indicating "Barring of Roaming", Error Diagnostic shall not be included.
    try:
        if not subscriber.roaming_allowed and \
           is_subscriber_roaming(request, check_remote_realm=True):
   
            app_counterdb.incr("ulr:num_answers:roaming_not_allowed")
    
            if subscriber.odb == "ODB-all-APN":
                #: test__ulr_route__7__diameter_error_roaming_not_allowed__odb_all_apn
                app_logger.debug(f"[{hbh}] Subscriber cannot roam due barred (ODB-all-APN): {imsi}")
                return r.roaming_not_allowed(ERROR_DIAGNOSTIC_ODB_ALL_APN)
            
            elif subscriber.odb == "ODB-HPLMN-APN":
                #: test__ulr_route__8__diameter_error_roaming_not_allowed__odb_hplmn_apn
                app_logger.debug(f"[{hbh}] Subscriber cannot roam due barred (ODB-HPLMN-APN): {imsi}")
                return r.roaming_not_allowed(ERROR_DIAGNOSTIC_ODB_HPLMN_APN)
            
            elif subscriber.odb == "ODB-VPLMN-APN":
                #: test__ulr_route__9__diameter_error_roaming_not_allowed__odb_vplmn_apn
                app_logger.debug(f"[{hbh}] Subscriber cannot roam due barred (ODB-HPLMN-APN): {imsi}")
                return r.roaming_not_allowed(ERROR_DIAGNOSTIC_ODB_VPLMN_APN)

    except DiameterInvalidAvpValue as e:
        #: test__ulr_route__13__diameter_realm_not_served
        app_counterdb.incr("ulr:num_answers:realm_not_served")
        app_logger.debug(f"[{hbh}] Found an invalid VPLMN realm: {e.args[0]}")
        return r.realm_not_served(e.args[0])


    #: If the Update Location Request is received over the S6a interface, and 
    #: the subscriber has not any APN configuration, the HSS shall return a 
    #: Result Code of DIAMETER_ERROR_UNKNOWN_EPS_SUBSCRIPTION. 
    if not subscriber.apns:
        app_counterdb.incr("ulr:num_answers:unknown_eps_subscription")
        app_logger.debug(f"[{hbh}] Subscriber does not have APN configuration: {imsi}")
        return r.unknown_eps_subscription()


    #: If the Update Location Request is received over the S6a interface, the
    #: HSS shall send a Cancel Location Request with a Cancellation-Type of
    #: MME_UPDATE_PROCEDURE (CLR; see chapter 7.2.7) to the previous MME (if
    #: any) and replace the stored MME-Identity with the received value (the 
    #: MME-Identity is received within the Origin-Host AVP). The HSS shall reset
    #: the "UE purged in MME" flag and delete any stored last known MME
    #: location information of the (no longer) purged UE.
    if is_new_mme_identity(request, subscriber):
        #: test__ulr_route__6__diameter_success__with_cancel_location_request
        clr = app.s6a.CLR(user_name=imsi,
                              cancellation_type=CANCELLATION_TYPE_MME_UPDATE_PROCEDURE,
                              destination_host=subscriber.mme_hostname)

        app.send_message(clr, recv_answer=False)
        app_logger.debug(f"[{hbh}] Sent CLR to MME")

    #: The HSS shall store the new terminal information and/or the new UE SRVCC
    #: capability, if they are present in the request. If the UE SRVCC 
    #: capability is not present, the HSS shall store that it has no knowledge
    #: of the UE SRVCC capability. 
    profile = {
        "mme_hostname": request.origin_host_avp.data.decode("utf-8"),
        "mme_realm": request.origin_realm_avp.data.decode("utf-8"),
        "ue_srvcc_support": is_ue_srvcc_supported(request),
    }
    update_mme_info_eps_subscription_profile(imsi, profile)

    #: test__ulr_route__4__diameter_success
    #: test__ulr_route__10__diameter_success__odb_all_apn
    #: test__ulr_route__11__diameter_success__odb_hplmn_apn
    #: test__ulr_route__12__diameter_success__odb_vplmn_apn
    app_counterdb.incr("ulr:num_answers:success")
    return r.success(subscription_data=create_subscription_data(subscriber))