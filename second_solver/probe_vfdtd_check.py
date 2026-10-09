# -*- coding: utf-8 -*-
"""probe_vfdtd_check.py — diagnose the varFDTD run: which results does the monitor expose?"""
from __future__ import annotations

import numpy as np


def check(mode) -> dict:
    rec = {}
    mode.switchtolayout()
    try:
        mode.select("monitor")
        rec["select_monitor"] = "OK"
    except Exception as exc:  # noqa: BLE001
        rec["select_monitor"] = "FAIL:" + str(exc).splitlines()[0][:40]
    for r in ("T", "power", "P", "T_forward", "transmission", "T_total", "T1"):
        try:
            v = mode.getresult("monitor", r)
            rec["monitor:" + r] = "OK shape=%s" % (np.array(v).shape,)
        except Exception as exc:  # noqa: BLE001
            rec["monitor:" + r] = "FAIL:" + str(exc).splitlines()[0][:45]
    for prov in ("varFDTD", "FDTD", "source"):
        for r in ("profile", "mode profile", "index", "effective index", "T"):
            try:
                v = mode.getresult(prov, r)
                rec[prov + ":" + r] = "OK shape=%s" % (np.array(v).shape,)
            except Exception as exc:  # noqa: BLE001
                rec[prov + ":" + r] = "FAIL:" + str(exc).splitlines()[0][:30]
    # read back key object positions so we know the model is as intended
    for name, prop in (("varFDTD", "x span"), ("varFDTD", "y span"), ("varFDTD", "simulation time"),
                       ("source", "x"), ("source", "y"), ("source", "injection axis"),
                       ("monitor", "x"), ("monitor", "monitor type")):
        try:
            rec["%s|%s" % (name, prop)] = str(np.array(mode.getnamed(name, prop)).ravel()[:2].tolist())
        except Exception as exc:  # noqa: BLE001
            rec["%s|%s" % (name, prop)] = "FAIL"
    return rec
