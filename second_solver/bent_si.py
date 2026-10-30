# -*- coding: utf-8 -*-
"""bent_si.py ??our case, built inside the vendor's working skeleton.

The vendor baseline (baseline_vendor.py) runs, so bent EME works here. This keeps that
construction and changes only what our case requires:
  * material: Si strip (n = 3.5), 0.5 x 0.22 um, centred in z, in SiO2
  * bend_radius = 10 um over a 15.708 um path  -> a quarter circle
  * target_neff 2.4 (the strip mode), no mode sweep, no port-mode storage (keeps the
    result file small; the S-matrix is all we need).
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
PATH = np.pi * R_BEND / 2.0        # quarter circle, in um
N_MODES = int(sys.argv[1]) if len(sys.argv) > 1 else 6
TAG = sys.argv[2] if len(sys.argv) > 2 else "si_R10_m%d" % N_MODES

strip = td.Structure(
    geometry=td.Box(center=(0, 0, 0), size=(1.5 * PATH, W, T_SI)),     # infinite, like the vendor file
    medium=td.Medium(permittivity=3.5 ** 2),
)

sim = td.EMESimulation(
    size=[PATH, 4, 4],
    freqs=[td.C_0 / LAM],
    axis=0,
    medium=td.Medium(permittivity=1.444 ** 2),                   # SiO2 cladding everywhere
    structures=[strip],
    grid_spec=td.GridSpec.uniform(dl=0.04),
    subpixel=td.SubpixelSpec(dielectric=td.PolarizedAveraging(), metal=td.Staircasing(),
                             pec=td.PECConformal(), pmc=td.Staircasing(),
                             lossy_metal=td.SurfaceImpedance()),
    eme_grid_spec=td.EMEUniformGrid(
        num_cells=6,
        mode_spec=td.EMEModeSpec(num_modes=N_MODES, target_neff=2.4, num_pml=[12, 12],
                                 bend_radius=R_BEND, bend_axis=1,
                                 sort_spec=td.ModeSortSpec(
                                     bounding_box={"center": [0, 0, 0], "size": [2 * PATH, W, T_SI]},
                                     sort_key="fill_fraction_box", sort_order="descending")),
    ),
    store_port_modes=False,
)

task_id = web.upload(sim, task_name=TAG, verbose=False)
cost = web.estimate_cost(task_id)
print("task %s  estimated %.4f" % (task_id, cost), flush=True)

data = web.run(sim, task_name=TAG, path=os.path.join(HERE, TAG + ".hdf5"), verbose=False)
sm = data.smatrix
S21 = np.abs(np.array(sm.S21)) ** 2
rec = {"tag": TAG, "modes": N_MODES, "R_um": R_BEND, "path_um": PATH, "estimate": cost,
       "colsum_21": np.round(S21.sum(axis=0), 6).tolist()}
print("column sums:", rec["colsum_21"], flush=True)

old = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else []
old.append(rec)
json.dump(old, open(OUT, "w", encoding="utf-8"), indent=1)
print("saved", OUT, flush=True)
