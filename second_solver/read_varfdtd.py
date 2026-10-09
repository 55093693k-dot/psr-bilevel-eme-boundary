# -*- coding: utf-8 -*-
"""read_varfdtd.py — read the varFDTD end-to-end transmission (monitor 'T')."""
from __future__ import annotations

import numpy as np


def read(mode) -> dict:
    rec = {}
    for prov in ("monitor", "power"):
        try:
            r = mode.getresult(prov, "T")
            if hasattr(r, "keys"):
                T = np.real(np.array(r["T"])).ravel()
                rec[prov] = {"T_mean": float(np.mean(T)), "T_min": float(np.min(T)),
                             "T_max": float(np.max(T)), "n": int(T.size)}
                if "lambda" in r.keys():
                    lam = np.real(np.array(r["lambda"])).ravel()
                    rec[prov]["lambda_nm"] = [float(lam.min() * 1e9), float(lam.max() * 1e9)]
            else:
                rec[prov] = str(r)[:80]
        except Exception as exc:  # noqa: BLE001
            rec[prov] = "FAIL:" + str(exc).splitlines()[0][:60]
    return rec
