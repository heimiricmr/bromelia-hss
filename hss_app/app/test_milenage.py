# -*- coding: utf-8 -*-
"""
    hss_app.test_milenage
    ~~~~~~~~~~~~~~~~~~~~~

    This module contains the Milenage algo unittests.
    
    :copyright: (c) 2021 Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

import unittest

from milenage import *
from utils import *


class TestMilenage(unittest.TestCase):
    def test__test_set_0(self):
        rand = bytes.fromhex("000000000000000000000000000008a7")
        opc = bytes.fromhex("cdc202d5123e20f62b6d676ac72cb318")
        key = bytes.fromhex("465b5ce8b199b49faa5f0a2ee238a6bc")
        amf = bytes.fromhex("8000")
        sqn = bytes.fromhex("000000000015")     # 21

        mac_a, mac_s= f1_and_f1_s(key, rand, opc, sqn, amf)
        xres, ak = f2_and_f5(key, rand, opc)
        ck = f3(key, rand, opc)
        ik = f4(key, rand, opc)
        f5_star = f5_s(key, rand, opc)

        self.assertEqual(mac_a.hex(), "aad7d3010fa706fb")                  # f1
        self.assertEqual(mac_s.hex(), "31661bccbd7e8fbe")                  # f1*
        self.assertEqual(xres.hex(), "c30ca0658493835c")                   # f2
        self.assertEqual(ck.hex(), "1fd124a000b7a19e7fb17bbd9defb9bc")     # f3
        self.assertEqual(ik.hex(), "5d62ae7a8f34508d5dafce8eff12caf7")     # f4
        self.assertEqual(ak.hex(), "a3216fff22c8")                         # f5
        self.assertEqual(f5_star.hex(), "70fbaa9aae10")                    # f5*

    def test__3gpp_35208_v5_0_0__test_set_1(self):
        rand = bytes.fromhex("23553cbe9637a89d218ae64dae47bf35")
        op = bytes.fromhex("cdc202d5123e20f62b6d676ac72cb318")
        key = bytes.fromhex("465b5ce8b199b49faa5f0a2ee238a6bc")
        amf = bytes.fromhex("b9b9")
        sqn = bytes.fromhex("ff9bb4d0b607")

        opc = generate_opc(key, op)
        self.assertEqual(opc.hex(), "cd63cb71954a9f4e48a5994e37a02baf")

        mac_a, mac_s= f1_and_f1_s(key, rand, opc, sqn, amf)
        xres, ak = f2_and_f5(key, rand, opc)
        ck = f3(key, rand, opc)
        ik = f4(key, rand, opc)
        f5_star = f5_s(key, rand, opc)

        self.assertEqual(mac_a.hex(), "4a9ffac354dfafb3")                  # f1
        self.assertEqual(mac_s.hex(), "01cfaf9ec4e871e9")                  # f1*
        self.assertEqual(xres.hex(), "a54211d5e3ba50bf")                   # f2
        self.assertEqual(ck.hex(), "b40ba9a3c58b2a05bbf0d987b21bf8cb")     # f3
        self.assertEqual(ik.hex(), "f769bcd751044604127672711c6d3441")     # f4
        self.assertEqual(ak.hex(), "aa689c648370")                         # f5
        self.assertEqual(f5_star.hex(), "451e8beca43b")                    # f5*

        # auts = calculate_auts(key, rand, opc, sqn, amf)
        # self.assertEqual(auts.hex(), "ba853f3c123c01cfaf9ec4e871e9")

        # sqn_ms, mac_s = generate_resync(key, rand, opc, auts, amf)
        # self.assertEqual(sqn_ms.hex(), "ff9bb4d0b607")
        # self.assertEqual(mac_s.hex(), "01cfaf9ec4e871e9")

    def test__3gpp_35208_v5_0_0__section_4_3_3__test_set_3(self):
        rand = bytes.fromhex("9f7c8d021accf4db213ccff0c7f71a6a")
        op = bytes.fromhex("dbc59adcb6f9a0ef735477b7fadf8374")
        key = bytes.fromhex("fec86ba6eb707ed08905757b1bb44b8f")
        amf = bytes.fromhex("725c")
        sqn = bytes.fromhex("9d0277595ffc")

        opc = generate_opc(key, op)
        self.assertEqual(opc.hex(), "1006020f0a478bf6b699f15c062e42b3")

        mac_a, mac_s= f1_and_f1_s(key, rand, opc, sqn, amf)
        xres, ak = f2_and_f5(key, rand, opc)
        ck = f3(key, rand, opc)
        ik = f4(key, rand, opc)
        f5_star = f5_s(key, rand, opc)

        self.assertEqual(mac_a.hex(), "9cabc3e99baf7281")                  # f1
        self.assertEqual(mac_s.hex(), "95814ba2b3044324")                  # f1*
        self.assertEqual(xres.hex(), "8011c48c0c214ed2")                   # f2
        self.assertEqual(ck.hex(), "5dbdbb2954e8f3cde665b046179a5098")     # f3
        self.assertEqual(ik.hex(), "59a92d3b476a0443487055cf88b2307b")     # f4
        self.assertEqual(ak.hex(), "33484dc2136b")                         # f5
        self.assertEqual(f5_star.hex(), "deacdd848cc6")                    # f5*

    def test__3gpp_35208_v5_0_0__section_4_3_4__test_set_4(self):
        rand = bytes.fromhex("ce83dbc54ac0274a157c17f80d017bd6")
        op = bytes.fromhex("223014c5806694c007ca1eeef57f004f")
        key = bytes.fromhex("9e5944aea94b81165c82fbf9f32db751")
        amf = bytes.fromhex("9e09")
        sqn = bytes.fromhex("0b604a81eca8")

        opc = generate_opc(key, op)
        self.assertEqual(opc.hex(), "a64a507ae1a2a98bb88eb4210135dc87")

        mac_a, mac_s= f1_and_f1_s(key, rand, opc, sqn, amf)
        xres, ak = f2_and_f5(key, rand, opc)
        ck = f3(key, rand, opc)
        ik = f4(key, rand, opc)
        f5_star = f5_s(key, rand, opc)

        self.assertEqual(mac_a.hex(), "74a58220cba84c49")                  # f1
        self.assertEqual(mac_s.hex(), "ac2cc74a96871837")                  # f1*
        self.assertEqual(xres.hex(), "f365cd683cd92e96")                   # f2
        self.assertEqual(ck.hex(), "e203edb3971574f5a94b0d61b816345d")     # f3
        self.assertEqual(ik.hex(), "0c4524adeac041c4dd830d20854fc46b")     # f4
        self.assertEqual(ak.hex(), "f0b9c08ad02e")                         # f5
        self.assertEqual(f5_star.hex(), "6085a86c6f63")                    # f5*

    def test__3gpp_35208_v5_0_0__section_4_3_5__test_set_5(self):
        rand = bytes.fromhex("74b0cd6031a1c8339b2b6ce2b8c4a186")
        op = bytes.fromhex("2d16c5cd1fdf6b22383584e3bef2a8d8")
        key = bytes.fromhex("4ab1deb05ca6ceb051fc98e77d026a84")
        amf = bytes.fromhex("9f07")
        sqn = bytes.fromhex("e880a1b5 80b6")

        opc = generate_opc(key, op)
        self.assertEqual(opc.hex(), "dcf07cbd51855290b92a07a9891e523e")

        mac_a, mac_s= f1_and_f1_s(key, rand, opc, sqn, amf)
        xres, ak = f2_and_f5(key, rand, opc)
        ck = f3(key, rand, opc)
        ik = f4(key, rand, opc)
        f5_star = f5_s(key, rand, opc)

        self.assertEqual(mac_a.hex(), "49e785dd12626ef2")                  # f1
        self.assertEqual(mac_s.hex(), "9e85790336bb3fa2")                  # f1*
        self.assertEqual(xres.hex(), "5860fc1bce351e7e")                   # f2
        self.assertEqual(ck.hex(), "7657766b373d1c2138f307e3de9242f9")     # f3
        self.assertEqual(ik.hex(), "1c42e960d89b8fa99f2744e0708ccb53")     # f4
        self.assertEqual(ak.hex(), "31e11a609118")                         # f5
        self.assertEqual(f5_star.hex(), "fe2555e54aa9")                    # f5*

    def test__3gpp_35208_v5_0_0__section_4_3_6__test_set_6(self):
        rand = bytes.fromhex("ee6466bc96202c5a557abbeff8babf63")
        op = bytes.fromhex("1ba00a1a7c6700ac8c3ff3e96ad08725")
        key = bytes.fromhex("6c38a116ac280c454f59332ee35c8c4f")
        amf = bytes.fromhex("4464")
        sqn = bytes.fromhex("414b98222181")

        opc = generate_opc(key, op)
        self.assertEqual(opc.hex(), "3803ef5363b947c6aaa225e58fae3934")

        mac_a, mac_s= f1_and_f1_s(key, rand, opc, sqn, amf)
        xres, ak = f2_and_f5(key, rand, opc)
        ck = f3(key, rand, opc)
        ik = f4(key, rand, opc)
        f5_star = f5_s(key, rand, opc)

        self.assertEqual(mac_a.hex(), "078adfb488241a57")                  # f1
        self.assertEqual(mac_s.hex(), "80246b8d0186bcf1")                  # f1*
        self.assertEqual(xres.hex(), "16c8233f05a0ac28")                   # f2
        self.assertEqual(ck.hex(), "3f8c7587fe8e4b233af676aede30ba3b")     # f3
        self.assertEqual(ik.hex(), "a7466cc1e6b2a1337d49d3b66e95d7b4")     # f4
        self.assertEqual(ak.hex(), "45b0f69ab06c")                         # f5
        self.assertEqual(f5_star.hex(), "1f53cd2b1113")                    # f5*

    def test__3gpp_35208_v5_0_0__section_4_3_7__test_set_7(self):
        rand = bytes.fromhex("194aa756013896b74b4a2a3b0af4539e")
        op = bytes.fromhex("460a48385427aa39264aac8efc9e73e8")
        key = bytes.fromhex("2d609d4db0ac5bf0d2c0de267014de0d")
        amf = bytes.fromhex("5f67")
        sqn = bytes.fromhex("6bf69438c2e4")

        opc = generate_opc(key, op)
        self.assertEqual(opc.hex(), "c35a0ab0bcbfc9252caff15f24efbde0")

        mac_a, mac_s= f1_and_f1_s(key, rand, opc, sqn, amf)
        xres, ak = f2_and_f5(key, rand, opc)
        ck = f3(key, rand, opc)
        ik = f4(key, rand, opc)
        f5_star = f5_s(key, rand, opc)

        self.assertEqual(mac_a.hex(), "bd07d3003b9e5cc3")                  # f1
        self.assertEqual(mac_s.hex(), "bcb6c2fcad152250")                  # f1*
        self.assertEqual(xres.hex(), "8c25a16cd918a1df")                   # f2
        self.assertEqual(ck.hex(), "4cd0846020f8fa0731dd47cbdc6be411")     # f3
        self.assertEqual(ik.hex(), "88ab80a415f15c73711254a1d388f696")     # f4
        self.assertEqual(ak.hex(), "7e6455f34cf3")                         # f5
        self.assertEqual(f5_star.hex(), "dc6dd01e8f15")                    # f5*


class TestGenerateEutranVector(unittest.TestCase):
    def test__test_set_0(self):
        rand = bytes.fromhex("000000000000000000000000000008a7")
        opc = bytes.fromhex("cdc202d5123e20f62b6d676ac72cb318")
        key = bytes.fromhex("465b5ce8b199b49faa5f0a2ee238a6bc")
        amf = bytes.fromhex("8000")
        sqn = bytes.fromhex("000000000015")     # 21
        plmn = bytes.fromhex("27f450")

        rand, xres, autn, kasme = calculate_eutran_vector(opc, key, amf, sqn, plmn, rand)

        self.assertEqual(xres.hex(), "c30ca0658493835c")
        self.assertEqual(autn.hex(), "a3216fff22dd8000aad7d3010fa706fb")
        self.assertEqual(kasme.hex(), "32ec19e7859f62bd096c55883aa16d1cfd94ac89a2ec6f7faaa69019623a7236")

    def test__3gpp_35208_v5_0_0__test_set_1(self):
        rand = bytes.fromhex("23553cbe9637a89d218ae64dae47bf35")
        opc = bytes.fromhex("cd63cb71954a9f4e48a5994e37a02baf")
        key = bytes.fromhex("465b5ce8b199b49faa5f0a2ee238a6bc")
        amf = bytes.fromhex("b9b9")
        sqn = bytes.fromhex("ff9bb4d0b607")
        plmn = bytes.fromhex("27f450")

        rand, xres, autn, kasme = calculate_eutran_vector(opc, key, amf, sqn, plmn, rand)

        self.assertEqual(xres.hex(), "a54211d5e3ba50bf")
        self.assertEqual(autn.hex(), "55f328b43577b9b94a9ffac354dfafb3")
        self.assertEqual(kasme.hex(), "00c73bac435945a7c5cf3565c0d3c64375416b255f0bd65d74f40e60c90a280a")

    def test__3gpp_35208_v5_0_0__section_4_3_3__test_set_3(self):
        rand = bytes.fromhex("9f7c8d021accf4db213ccff0c7f71a6a")
        opc = bytes.fromhex("1006020f0a478bf6b699f15c062e42b3")
        key = bytes.fromhex("fec86ba6eb707ed08905757b1bb44b8f")
        amf = bytes.fromhex("725c")
        sqn = bytes.fromhex("9d0277595ffc")
        plmn = bytes.fromhex("27f450")

        rand, xres, autn, kasme = calculate_eutran_vector(opc, key, amf, sqn, plmn, rand)

        self.assertEqual(xres.hex(), "8011c48c0c214ed2")
        self.assertEqual(autn.hex(), "ae4a3a9b4c97725c9cabc3e99baf7281")
        self.assertEqual(kasme.hex(), "4826154dc86a76e8eeba9673c5c7fac9141f00c0c0ffbf386e93e9f2e0eb34f4")

    def test__3gpp_35208_v5_0_0__section_4_3_4__test_set_4(self):
        rand = bytes.fromhex("ce83dbc54ac0274a157c17f80d017bd6")
        opc = bytes.fromhex("a64a507ae1a2a98bb88eb4210135dc87")
        key = bytes.fromhex("9e5944aea94b81165c82fbf9f32db751")
        amf = bytes.fromhex("9e09")
        sqn = bytes.fromhex("0b604a81eca8")
        plmn = bytes.fromhex("27f450")

        rand, xres, autn, kasme = calculate_eutran_vector(opc, key, amf, sqn, plmn, rand)

        self.assertEqual(xres.hex(), "f365cd683cd92e96")
        self.assertEqual(autn.hex(), "fbd98a0b3c869e0974a58220cba84c49")
        self.assertEqual(kasme.hex(), "35e1f31c813e4b64466367bf15b6e52b7db7cd9922901bd793432be30d754f6a")

    def test__3gpp_35208_v5_0_0__section_4_3_5__test_set_5(self):
        rand = bytes.fromhex("74b0cd6031a1c8339b2b6ce2b8c4a186")
        opc = bytes.fromhex("dcf07cbd51855290b92a07a9891e523e")
        key = bytes.fromhex("4ab1deb05ca6ceb051fc98e77d026a84")
        amf = bytes.fromhex("9f07")
        sqn = bytes.fromhex("e880a1b5 80b6")
        plmn = bytes.fromhex("27f450")

        rand, xres, autn, kasme = calculate_eutran_vector(opc, key, amf, sqn, plmn, rand)

        self.assertEqual(xres.hex(), "5860fc1bce351e7e")
        self.assertEqual(autn.hex(), "d961bbd511ae9f0749e785dd12626ef2")
        self.assertEqual(kasme.hex(), "788677b1a220a418640338c8d6a8d6dbc306ea2a239154460084259b53c82a83")

    def test__3gpp_35208_v5_0_0__section_4_3_6__test_set_6(self):
        rand = bytes.fromhex("ee6466bc96202c5a557abbeff8babf63")
        opc = bytes.fromhex("3803ef5363b947c6aaa225e58fae3934")
        key = bytes.fromhex("6c38a116ac280c454f59332ee35c8c4f")
        amf = bytes.fromhex("4464")
        sqn = bytes.fromhex("414b98222181")
        plmn = bytes.fromhex("27f450")

        rand, xres, autn, kasme = calculate_eutran_vector(opc, key, amf, sqn, plmn, rand)

        self.assertEqual(xres.hex(), "16c8233f05a0ac28")
        self.assertEqual(autn.hex(), "04fb6eb891ed4464078adfb488241a57")
        self.assertEqual(kasme.hex(), "2a90f8b6b6522d62f046f838693c4946edcdc52eeabf1204e275eb1d53853b69")

    def test__3gpp_35208_v5_0_0__section_4_3_7__test_set_7(self):
        rand = bytes.fromhex("194aa756013896b74b4a2a3b0af4539e")
        opc = bytes.fromhex("c35a0ab0bcbfc9252caff15f24efbde0")
        key = bytes.fromhex("2d609d4db0ac5bf0d2c0de267014de0d")
        amf = bytes.fromhex("5f67")
        sqn = bytes.fromhex("6bf69438c2e4")
        plmn = bytes.fromhex("27f450")

        rand, xres, autn, kasme = calculate_eutran_vector(opc, key, amf, sqn, plmn, rand)

        self.assertEqual(xres.hex(), "8c25a16cd918a1df")
        self.assertEqual(autn.hex(), "1592c1cb8e175f67bd07d3003b9e5cc3")
        self.assertEqual(kasme.hex(), "8cd327e3d1eba71cbc7b3e84a7dbfc88038ccd1adb530415d96d9201056a682c")


if __name__ == "__main__":
    unittest.main()