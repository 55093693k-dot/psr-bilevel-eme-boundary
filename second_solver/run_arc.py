# -*- coding: utf-8 -*-
"""run_arc.py — run ONE bent-cell variant and read the column sums.

Usage:  python run_arc.py <tag> <bend_axis> <num_cells>
Launched detached (the cloud solve outlasts a shell call). It appends one record to
arc_results.json as soon as it has an answer, and prints the S-matrix structure so the
extraction is checked rather than assumed.
"""
import json
import os
import sys

import numpy as np

import tidy3d.web as web

import bentcell_arc as arc

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "arc_results.json")

tag = sys.argv[1] if len(sys.argv) > 1 else "bent_axis0"
axis = int(sys.argv[2]) if len(sys.argv) > 2 else 0
cells = int(sys.argv[3]) if len(sys.argv) > 3 else 8
store_modes = int(sys.argv[4]) if len(sys.argv) > 4 else 1

sim = arc.bent(cells, bend_axis=axis, store_port_modes=(store_modes == 1))
sim.validate_pre_upload()
task_id = web.upload(sim, task_name=tag, verbose=False)
cost = web.estimate_cost(task_id)
print("task %s  estimated %.4f" % (task_id, cost), flush=True)

data = web.run(sim, task_name=tag, path=os.path.join(HERE, tag + ".hdf5"), verbose=False)
rec = {"tag": tag, "bend_axis": axis, "cells": cells, "task": task_id, "estimate": cost}
sm = getattr(data, "smatrix", None)
print("data:", type(data).__name__, "| smatrix:", type(sm).__name__ if sm is not None else None, flush=True)
if sm is not None:
    for name in ("S11", "S12", "S21", "S22"):
        arr = getattr(sm, name, None)
        if arr is not None:
            print(name, np.array(arr).shape, flush=True)
    S21 = np.abs(np.array(sm.S21)) ** 2
    S11 = np.abs(np.array(sm.S11)) ** 2
    rec["colsum_21"] = np.round(S21.sum(axis=0), 6).tolist()
    rec["colsum_11"] = np.round(S11.sum(axis=0), 6).tolist()
    print("column sums S21 (per input mode):", rec["colsum_21"], flush=True)
    print("column sums S11 (per input mode):", rec["colsum_11"], flush=True)

old = []
if os.path.exists(OUT):
    with open(OUT, encoding="utf-8") as fh:
        old = json.load(fh)
old.append(rec)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(old, fh, indent=1)
print("appended to", OUT, flush=True)
