# -*- coding: utf-8 -*-
"""run_arcs_all.py — the like-for-like comparison on ONE 90-degree arc of R = 10 um.

Arm A (bent cells): the structure is straight, each EME cell carries bend_radius. Two cell
counts, to show the reading does not depend on how many cells the arc is cut into.
Arm B (straight cells): the same arc drawn as a staircase of N boxes, i.e. exactly what a
user does when the tool has no bent cells. Swept over cell length.

All runs share: Si 0.5 x 0.22 um in SiO2, lambda 1.55 um, uniform cross-section mesh
dl = 0.04 um, 6 modes with 12 PML layers, target neff 2.4.
Each record is appended to arc_results.json as soon as it lands.
"""
import json
import os
import sys

import numpy as np

import tidy3d as td
import tidy3d.web as web

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "arc_results.json")

LAM = 1.55e-6
W, T_SI = 0.5, 0.22
R_BEND = 10.0
PATH = np.pi * R_BEND / 2.0
N_MODES = 6
SI = td.Medium(permittivity=3.5 ** 2)
SIO2 = td.Medium(permittivity=1.444 ** 2)


def _sim(structures, cells, bend_radius=None):
    spec = dict(num_modes=N_MODES, target_neff=2.4, num_pml=[12, 12])
    if bend_radius is not None:
        spec.update(bend_radius=bend_radius, bend_axis=1)
    return td.EMESimulation(
        size=[PATH, 4, 4],
        freqs=[td.C_0 / LAM],
        axis=0,
        medium=SIO2,
        structures=structures,
        grid_spec=td.GridSpec.uniform(dl=0.04),
        eme_grid_spec=td.EMEUniformGrid(num_cells=cells, mode_spec=td.EMEModeSpec(**spec)),
        store_port_modes=False,
    )


def arm_bent(cells):
    strip = td.Structure(geometry=td.Box(center=(0, 0, 0), size=(1.5 * PATH, W, T_SI)), medium=SI)
    return _sim([strip], cells, bend_radius=R_BEND)


def arm_staircase(cell_um):
    """The same quarter circle, cut into `cell_um` steps and drawn as boxes."""
    n = max(4, int(round(PATH / cell_um)))
    step = PATH / n
    boxes = []
    for i in range(n):
        s = -PATH / 2 + (i + 0.5) * step          # position along the arc
        phi = s / R_BEND
        cx, cy = R_BEND * np.sin(phi), R_BEND * (1 - np.cos(phi))
        boxes.append(td.Structure(geometry=td.Box(center=(cx, cy, 0), size=(1.05 * step, W, T_SI)),
                                  medium=SI))
    return _sim(boxes, n)


def run(sim, tag):
    task_id = web.upload(sim, task_name=tag, verbose=False)
    cost = web.estimate_cost(task_id)
    data = web.run(sim, task_name=tag, path=os.path.join(HERE, tag + ".hdf5"), verbose=False)
    s21 = np.abs(np.array(data.smatrix.S21)) ** 2
    col = np.array(s21).reshape(-1, np.array(s21).shape[-2], np.array(s21).shape[-1])
    sums = col.sum(axis=-2)[0]                   # sum over output modes, first frequency
    rec = {"tag": tag, "estimate": cost, "colsum": [round(float(x), 6) for x in sums]}
    print("RESULT", json.dumps(rec), flush=True)
    old = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else []
    old.append(rec)
    json.dump(old, open(OUT, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "bent12"):
        run(arm_bent(12), "bent_c12")
    if which in ("all", "stairs"):
        for c in (5.0, 2.5, 1.0):
            run(arm_staircase(c), "stairs_%gum".replace("%g", str(c)))
