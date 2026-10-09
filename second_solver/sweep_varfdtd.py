# -*- coding: utf-8 -*-
"""sweep_varfdtd.py — does the varFDTD bend transmission scale with the lateral offset?

varFDTD gives straight ~0.976 and S-bend ~0.69 (invariant to mesh). Sweep the bend offset down
toward the straight, to see whether the "loss" scales with the lateral movement (the signature the
EME also showed) or is a flat offset.
"""
from __future__ import annotations

import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_ns = {}
exec(compile(open(os.path.join(HERE, "ready_varfdtd.py"), encoding="utf-8").read(),
             "ready_varfdtd.py", "exec"), _ns)
build = _ns["build"]


def run(mode, dys_um=(5.0, 2.0, 1.0)) -> dict:
    out = {}
    for d in dys_um:
        build(mode, dy=d * 1e-6, save_path=os.path.join(HERE, "sweep_dy%g.lms" % d))
        mode.select("varFDTD")
        mode.run()
        try:
            r = mode.getresult("monitor", "T")
            out["dy%gum" % d] = float(np.mean(np.real(np.array(r["T"])).ravel()))
        except Exception as exc:  # noqa: BLE001
            out["dy%gum" % d] = "FAIL:" + str(exc).splitlines()[0][:40]
    return out
