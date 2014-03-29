# Test cases for VHT operations with hostapd
# Copyright (c) 2014, Qualcomm Atheros, Inc.
# Copyright (c) 2013, Intel Corporation
#
# This software may be distributed under the terms of the BSD license.
# See README for more details.

import logging
logger = logging.getLogger()
import subprocess, time

import hwsim_utils
import hostapd

def vht_supported():
    cmd = subprocess.Popen(["iw", "reg", "get"], stdout=subprocess.PIPE)
    reg = cmd.stdout.read()
    if "@ 80)" in reg or "@ 160)" in reg:
        return True
    return False

def test_ap_vht80(dev, apdev):
    """VHT with 80 MHz channel width"""
    try:
        params = { "ssid": "vht",
                   "country_code": "FI",
                   "hw_mode": "a",
                   "channel": "36",
                   "ht_capab": "[HT40+]",
                   "ieee80211n": "1",
                   "ieee80211ac": "1",
                   "vht_oper_chwidth": "1",
                   "vht_oper_centr_freq_seg0_idx": "42" }
        hapd = hostapd.add_ap(apdev[0]['ifname'], params)

        dev[0].connect("vht", key_mgmt="NONE", scan_freq="5180")
        hwsim_utils.test_connectivity(dev[0].ifname, apdev[0]['ifname'])
    except Exception, e:
        if isinstance(e, Exception) and str(e) == "AP startup failed":
            if not vht_supported():
                logger.info("80 MHz channel not supported in regulatory information")
                return "skip"
        raise
    finally:
        subprocess.call(['sudo', 'iw', 'reg', 'set', '00'])

def test_ap_vht80_params(dev, apdev):
    """VHT with 80 MHz channel width and number of optional features enabled"""
    try:
        params = { "ssid": "vht",
                   "country_code": "FI",
                   "hw_mode": "a",
                   "channel": "36",
                   "ht_capab": "[HT40+][SHORT-GI-40][DSS_CCK-40]",
                   "ieee80211n": "1",
                   "ieee80211ac": "1",
                   "vht_oper_chwidth": "1",
                   "vht_capab": "[MAX-MPDU-11454][RXLDPC][SHORT-GI-80][TX-STBC-2BY1][RX-STBC-1][MAX-A-MPDU-LEN-EXP0]",
                   "vht_oper_centr_freq_seg0_idx": "42",
                   "require_vht": "1" }
        hapd = hostapd.add_ap(apdev[0]['ifname'], params)

        dev[1].connect("vht", key_mgmt="NONE", scan_freq="5180",
                       disable_vht="1", wait_connect=False)
        dev[0].connect("vht", key_mgmt="NONE", scan_freq="5180")
        ev = dev[1].wait_event(["CTRL-EVENT-ASSOC-REJECT"])
        if ev is None:
            raise Exception("Association rejection timed out")
        if "status_code=104" not in ev:
            raise Exception("Unexpected rejection status code")
        dev[1].request("DISCONNECT")
        hwsim_utils.test_connectivity(dev[0].ifname, apdev[0]['ifname'])
    except Exception, e:
        if isinstance(e, Exception) and str(e) == "AP startup failed":
            if not vht_supported():
                logger.info("80 MHz channel not supported in regulatory information")
                return "skip"
        raise
    finally:
        subprocess.call(['sudo', 'iw', 'reg', 'set', '00'])

def test_ap_vht_20(devs, apdevs):
    dev = devs[0]
    ap = apdevs[0]
    try:
        params = { "ssid": "test-vht20",
                   "country_code": "DE",
                   "hw_mode": "a",
                   "channel": "36",
                   "ieee80211n": "1",
                   "ieee80211ac": "1",
                   "ht_capab": "",
                   "vht_capab": "",
                   "vht_oper_chwidth": "0",
                   "vht_oper_centr_freq_seg0_idx": "0",
                   "supported_rates": "60 120 240 360 480 540",
                   "require_vht": "1",
                 }
        hostapd.add_ap(ap['ifname'], params)
        dev.connect("test-vht20", scan_freq="5180", key_mgmt="NONE")
        hwsim_utils.test_connectivity(dev.ifname, ap['ifname'])
    finally:
        subprocess.call(['sudo', 'iw', 'reg', 'set', '00'])