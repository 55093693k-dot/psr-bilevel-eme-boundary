# -*- coding: utf-8 -*-
"""refine_amp.py — push the amplified-bend cell ladder below 0.5 um.

WHY THIS FILE EXISTS
--------------------
The manuscript's cell clause says the reading is lifted by refining the cells until it
stops changing, and it reports that it has NOT stopped at 0.5 um. A referee's first
question is "how fine is enough, then?". Neither shipped ladder answers it: the device
ladder stops at 0.75 um because the solver rejects >500 EME cells on the 300 um domain,
and the amplified-bend ladder stops at 0.5 um because that is where the previous round
stopped looking, not because of a limit.

The amplified model is only 60 um long, so 240 cells (0.25 um) and 480 cells (0.125 um)
are both inside the solver's 500-cell limit. This script extends the ladder there, on the
same model, same platform and same basis as the recorded runs, and reports the wall time.

The geometry is NOT retyped: it is built by probe_amp._build, so it cannot drift from the
runs the manuscript quotes.

READ-OUT
--------
column sum = sum over output-port modes of |S|^2 for each input mode, at 8 port modes
(default) or 32. Values are rounded to 6 decimals, as in the recorded runs.
"""
from __future__ import annotations

import json
import os
import time

import numpy as np

import probe_amp as pa

SAVE = os.path.dirname(os.path.abspath(__file__))


def points(mode, cells_um, modes=8, dy=5e-6, l_str=20e-6, l_bend=20e-6):
    """Run one point per cell length; return a list of records."""
    L = 2 * l_str + l_bend
    out = []
    for c in cells_um:
        cells = int(round(L / (c * 1e-6)))
        t0 = time.time()
        rec = {"cell_um": c, "cells": cells, "modes": modes}
        try:
            pa._build(mode, dy=dy, l_str=l_str, l_bend=l_bend, modes=modes, cells=cells)
            mode.save(os.path.join(SAVE, "refine_bend%g_m%d_cell%g.lms" % (l_bend * 1e6, modes, c)))
            mode.select("EME")
            mode.run()
            mode.emepropagate()
            got = mode.getresult("EME", "user s matrix")
            arr = np.array(got["S"]) if (hasattr(got, "keys") and "S" in got.keys()) else np.array(got)
            a2 = np.abs(arr) ** 2
            rec["colsum"] = np.round(a2.sum(axis=0), 6).tolist()
        except Exception as exc:  # noqa: BLE001
            rec["error"] = str(exc).splitlines()[0][:80]
        rec["wall_s"] = round(time.time() - t0, 1)
        out.append(rec)
        print(json.dumps(rec))
    return out


def write(records, name="refine_amp_results.json"):
    path = os.path.join(SAVE, name)
    old = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            old = json.load(fh)
    old.extend(records)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(old, fh, indent=1)
    return path
