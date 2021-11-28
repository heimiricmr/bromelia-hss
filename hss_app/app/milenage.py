# -*- coding: utf-8 -*-
"""
    hss_app.milenage
    ~~~~~~~~~~~~~~~~

    This module implements the Milenage algo set as per
    3GPP TS 35.206 V9.0.0 (2009-12).

"""

import hmac
import random
from collections import namedtuple

from Crypto.Cipher import AES

AMF_DEFAULT_VALUE = bytes.fromhex("8000")
INITIALIZATION_VECTOR = 16 * bytes.fromhex("00")

#: Five 128-bit constants c1, c2, c3, c4, c5 are defined as per 
#: ETSI TS 135 206 V9.0.0 (2010-02) in Section 4.1.

C1 = 16 * bytes.fromhex("00")                       # 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00
C2 = 15 * bytes.fromhex("00") + bytes.fromhex("01") # 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x01
C3 = 15 * bytes.fromhex("00") + bytes.fromhex("02") # 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x02
C4 = 15 * bytes.fromhex("00") + bytes.fromhex("04") # 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x04
C5 = 15 * bytes.fromhex("00") + bytes.fromhex("08") # 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x08

R1 = 8                                              # rotate by 8 * 8 = 64 bits
R2 = 0                                              # rotate by 0 * 8 = 0 bits
R3 = 4                                              # rotate by 4 * 8 = 32 bits
R4 = 8                                              # rotate by 8 * 8 = 64 bits
R5 = 12                                             # rotate by 12 * 8 = 96 bits

#: Constants defined as per ETSI TS 133 401 V15.7.0 (2019-05) in Annex A.2 
#: KASME derivation function
FC = bytes.fromhex("10")                            # 0x10
L0 = bytes.fromhex("0003")                          # 0x00 0x03
L1 = bytes.fromhex("0006")                          # 0x00 0x06

Vector = namedtuple("Vector", ["rand", "xres", "autn", "kasme"])


def xor(bytes1: bytes, bytes2: bytes) -> bytes:
    """Support function to perform Exclusive-OR operation on two bytes.

    :param bytes1: set of bytes 1
    :param bytes2: set of bytes 2

    :returns: XORed data
    """
    if len(bytes1) == len(bytes2):
        return bytes(a ^ b for a, b in zip(bytes1, bytes2))
    raise ValueError("Input values must have same length")


def rot(_input: bytes, _bytes: int) -> bytes:
    """Support function to rotate a byte stream by a given byte value.

    :param _input: bytes stream
    :param _bytes: bytes to be rotated

    :returns: rotated data
    """
    return bytes(_input[(i + _bytes) % len(_input)] for i in range(len(_input)))


def kdf(key: bytes, data: bytes) -> bytes:
    """Implementation of Generic Key Derivation Function in Annex B.2 of 
    ETSI TS 133 220 V11.4.0 (2012-10).

    :param key: denoted key
    :param data: data to be hashed

    :returns: derived key, the hashed data
    """
    return hmac.new(key, data, "sha256").digest()


def cipher(key: bytes, data: bytes, IV: bytes = INITIALIZATION_VECTOR) -> bytes:
    """Implementation of Rijndael (AES-128) encryption function used by
    Milenage algo.

    :param key: 128-bit subscriber key
    :param data: 128-bit data to be encripted
    :param IV: 128-bit initialization vector

    :returns: encrypted data
    """
    aes_cipher = AES.new(key, AES.MODE_CBC, IV)
    return aes_cipher.encrypt(data)


def calculate_autn(sqn: bytes, ak: bytes, mac_a: bytes, amf: bytes = AMF_DEFAULT_VALUE) -> bytes:
    """Implementation of network authentication token calculation in 
    Section 5.1.1.1 of 3GPP TS 33.105 V13.0.0 (2016-01).

    :param sqn: 48-bit sequence number
    :param ak: 48-bit anonymity key
    :param mac_a: 64-bit network authentication code
    :param amf: 16-bit authentication management field

    :returns: authentication token of 128 bits (AUTN)
    """
    return xor(sqn, ak) + amf + mac_a


def calculate_kasme(ck: bytes, ik: bytes, plmn: bytes, sqn: bytes, ak: bytes) -> bytes:
    """Implementation of Kasme derivation function in Annex A.2 of
    ETSI TS 133 401 V15.7.0 (2019-05).

    :param ck: 32-bit confidentiality key
    :param ik: 32-bit integrity key
    :param plmn: 24-bit network identifier
    :param sqn: 48-bit sequence number
    :param ak: 48-bit anonymity key

    :returns: 128-bit network base key
    """
    return kdf(ck + ik, (FC + plmn + L0 + xor(sqn, ak) + L1))


def generate_opc(key: bytes, op: bytes) -> bytes:
    """Implementation of OPc computation in Section 8.2 of
    3GPP TS 35.205 V5.0.0 (2002-06).

    :param key: 128-bit subscriber key
    :param op: 128-bit Operator Variant Algorithm Configuration Field

    :returns: 128-bit value derived from OP & K used within the computation of the functions
    """
    return xor(cipher(key, op), op)


def generate_rand() -> bytes:
    """Function that generates a 128-bit random challenge (RAND) for Milenage
    algo.

    :returns: 128-bit random challenge (RAND)
    """
    return bytes(bytearray.fromhex("{:032x}".format(random.getrandbits(128))))


def calculate_output(key: bytes, rand: bytes, opc: bytes, r: int, c: bytes, sqn: bytes = None, amf: bytes = None) -> bytes:
    """Support function which represent the common operations along the set of 
    3GPP authentication and key generation functions f1, f1*, f2, f3, f4, f5 and
    f5*.

    :param key: 128-bit subscriber key
    :param rand: 128-bit random challenge
    :param opc: 128-bit value derived from OP & K
    :param r: integers in the range 0–127 inclusive, which define amounts by which intermediate variables are cyclically rotated
    :param c: 128-bit constants, which are XORed onto intermediate variables
    :param sqn: 48-bit sequence number
    :param amf: 16-bit authentication management field

    :returns: output corresponding to 3GPP authentication function triggered
    """
    if sqn is None and amf is None:
        temp = xor(cipher(key, xor(rand, opc)), opc)
        return xor(cipher(key, xor(rot(temp, r), c)), opc)

    temp = cipher(key, xor(rand, opc))
    in1 = (sqn[0:6] + amf[0:2]) * 2
    return xor(opc, cipher(key, xor(temp, rot(xor(in1, opc), R1)), C1))


def get_mac_a(output: bytes) -> bytes:
    """Support function to get the 64-bit network authentication code (MAC-A)
    from OUT1, the output of 3GPP f1 function.

    :param output: OUT1

    :returns: OUT1[0] .. OUT1[63]
    """
    edge = 8 # = ceil(63/8)
    return output[:edge]


def get_mac_s(output: bytes) -> bytes:
    """Support function to get the 64-bit resynchronisation authentication code
    (MAC-S) from OUT1, the output of 3GPP f1* function.

    :param output: OUT1

    :returns: OUT1[64] .. OUT1[127]
    """
    edge = 8 # = ceil(63/8)
    return output[edge:]


def get_res(output: bytes) -> bytes:
    """Support function to get the 64-bit signed response (RES) from OUT2, the
    output of 3GPP f2 function.

    :param output: OUT2

    :returns: OUT2[64] .. OUT2[127]
    """
    lower_edge = 8  # = ceil(64/8)
    upper_edge = 16 # = ceil(127/8)
    return output[lower_edge:upper_edge]


def get_ak(output: bytes) -> bytes:
    """Support function to get the 48-bit anonimity key (AK) from OUT2, the
    output of 3GPP f5 function.

    :param output: OUT2

    :returns: OUT2[0] .. OUT2[47]
    """
    edge = 6 # = ceil(47/8)
    return output[:edge]


def f1_and_f1_s(key: bytes, rand: bytes, opc: bytes, sqn: bytes, amf: bytes) -> bytes:
    """Implementation of key generation function f1 & f1* in Section 4.1 of
    3GPP TS 35.206 V9.0.0 (2009-12), which calculates the authentication code
    (MAC-A) and resynchronization authentication code (MAC-S) respectively.

    :param key: 128-bit subscriber key
    :param rand: 128-bit random challenge
    :param opc: 128-bit value derived from OP & K
    :param sqn: 48-bit sequence number
    :param amf: 16-bit authentication management field

    :returns:
        - mac_a - 64-bit network authentication code (MAC-A)
        - mac_s - 64-bit resynchronisation authentication code (MAC-S)
    """
    output = calculate_output(key, rand, opc, R1, C1, sqn, amf)
    return get_mac_a(output), get_mac_s(output)


def f2_and_f5(key: bytes, rand: bytes, opc: bytes) -> bytes:
    """Implementation of key generation functions f2 & f5 in Section 4.1 of 
    3GPP TS 35.206 V9.0.0 (2009-12), which calculates the result (RES) and 
    anonymity key (AK) respectively.

    :param key: 128-bit subscriber key
    :param rand: 128-bit random challenge
    :param opc: 128-bit value derived from OP & K

    :returns:
        - res - 64-bit signed response (RES)
        - ak - 48-bit anonymity key (AK)
    """
    output = calculate_output(key, rand, opc, R2, C2)
    return get_res(output), get_ak(output)


def f3(key: bytes, rand: bytes, opc: bytes) -> bytes:
    """Implementation of key generation function f3 in Section 4.1 of 
    3GPP TS 35.206 V9.0.0 (2009-12), which calculates the confidentiality key
    (CK).

    :param key: 128-bit subscriber key
    :param rand: 128-bit random challenge
    :param opc: 128-bit value derived from OP & K

    :returns: 128-bit confidentiality key (CK)
    """
    return calculate_output(key, rand, opc, R3, C3)


def f4(key: bytes, rand: bytes, opc: bytes) -> bytes:
    """Implementation of key generation function f4 in Section 4.1 of 
    3GPP TS 35.206 V9.0.0 (2009-12), which calculates the integrity key (IK).

    :param key: 128-bit subscriber key
    :param rand: 128-bit random challenge
    :param opc: 128-bit value derived from OP & K

    :returns: 128-bit integrity key (IK)
    """
    return calculate_output(key, rand, opc, R4, C4)


def get_f5_s(output: bytes) -> bytes:
    """Support function to get the 48-bit anonimity key (AK) from OUT5, the
    output of 3GPP f5* function.

    :param output: OUT5

    :returns: OUT5[0] .. OUT5[47]
    """
    edge = 6 # = ceil(47/8)
    return output[:edge]


def f5_s(key: bytes, rand: bytes, opc: bytes) -> bytes:
    """Implementation of key generation function f5* in Section 4.1 of 
    3GPP TS 35.206 V9.0.0 (2009-12), which calculates the anonymity key (AK).

    :param key: 128-bit subscriber key
    :param rand: 128-bit random challenge
    :param opc: 128-bit value derived from OP & K

    :returns: 128-bit anonymity key (AK)
    """
    output = calculate_output(key, rand, opc, R5, C5)
    return get_f5_s(output)


def calculate_eutran_vector(opc: bytes, key: bytes, amf: bytes, sqn: bytes, plmn: bytes, rand: bytes = None) -> Vector:
    """Implementation of E-UTRAN vector calculation based on Milenage algo set.

    :param opc: 128-bit value derived from OP & K
    :param key: 128-bit subscriber key
    :param amf: 16-bit authentication management field
    :param sqn: 48-bit sequence number
    :param plmn: 24-bit network identifier
    :param rand: 128-bit random challenge

    :returns: Vector namedtuple
    """
    if rand is None:
        rand = generate_rand()

    mac_a, _ = f1_and_f1_s(key, rand, opc, sqn, amf)
    xres, ak = f2_and_f5(key, rand, opc)
    ck = f3(key, rand, opc)
    ik = f4(key, rand, opc)
    autn = calculate_autn(sqn, ak, mac_a, amf)
    kasme = calculate_kasme(ck, ik, plmn, sqn, ak)

    return Vector(bytes(rand), bytes(xres), bytes(autn), bytes(kasme))