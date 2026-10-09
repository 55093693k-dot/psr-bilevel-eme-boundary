# -*- coding: utf-8 -*-
"""probe_vei.py — discover the varFDTD effective-index settings on this install.

The varFDTD bend gave ~0.69 vs a straight reference of ~0.98, while the exact FDE bent-mode solve
says the bend is lossless. varFDTD derives its 2D effective materials from a reference slab mode;
those settings were left at defaults. This lists which of them the object actually exposes.
"""
from __future__ import annotations

import numpy as np


def probe(mode) -> dict:
    mode.switchtolayout()
    rec = {}
    props = ["slab mode position", "slab mode", "slab mode position x", "slab mode position y",
             "slab mode position z", "slab mode x", "slab mode y", "slab mode z",
             "polarization", "mode selection", "effective index method",
             "simulation bandwidth", "bandwidth", "simulation bandwidth mode",
             "clamp to physical material properties", "clamp materials",
             "test points", "define test points", "mesh accuracy",
             "use max index", "background material", "background index",
             "calculate effective index", "effective index resolution",
             "meshing refinement", "use mesh refinement", "define x mesh by"]
    for p in props:
        try:
            v = mode.getnamed("varFDTD", p)
            rec[p] = str(np.array(v).ravel()[:3].tolist())
        except Exception as exc:  # noqa: BLE001
            rec[p] = "FAIL:" + str(exc).splitlines()[0][:32]
    return rec
