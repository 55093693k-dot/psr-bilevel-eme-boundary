# -*- coding: utf-8 -*-
"""probe_mesh.py — lateral-offset sweep of the minimal S-bend column-sum.

Originally written to sweep the transverse mode-solver mesh, but the EME object's dx/dy/dz are
READ-ONLY ("inactive" under setnamed), so that knob cannot be moved from script. Repurposed to
sweep the bend's total lateral offset dy (0.5 -> 5 um) at a FIXED 5 um cell length and 5 modes,
to see how the column-sum depends on the offset itself. Run through the persistent MODE process.
"""
from __future__ import annotations

import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "probe_projects")
L_TOT = 200e-6
L_BEND = 100e-6
L_STRAIGHT = 50e-6
W = 0.50e-6
T_SI = 0.22e-6


def _verts(dy: float, n: int = 401) -> np.ndarray:
    x = np.linspace(0.0, L_TOT, n)
    y = np.zeros_like(x)
    inb = (x > L_STRAIGHT) & (x < L_STRAIGHT + L_BEND)
    y[inb] = dy * (1 - np.cos(np.pi * (x[inb] - L_STRAIGHT) / L_BEND)) / 2.0
    y[x >= L_STRAIGHT + L_BEND] = dy
    th = np.arctan(np.gradient(y, x))
    nx, ny = -np.sin(th), np.cos(th)
    top = np.vstack([x + nx * W / 2, y + ny * W / 2]).T
    bot = np.vstack([x - nx * W / 2, y - ny * W / 2]).T
    return np.vstack([top, bot[::-1]])


def run(mode, dy_list=(0.5e-6, 1.0e-6, 2.0e-6, 3.0e-6, 5.0e-6), modes: int = 8,
        cell: float = 5.0e-6) -> list:
    cells = int(round(L_TOT / cell))
    out = []
    for dy in dy_list:
        mode.switchtolayout()
        mode.deleteall()
        mode.addrect(x=L_TOT / 2, y=dy / 2, z=-0.5e-6, x_span=L_TOT, y_span=dy + 6e-6,
                     z_span=1e-6, material="SiO2 (Glass) - Palik")
        p = mode.addpoly(x=0, y=0, z=T_SI / 2, z_span=T_SI, material="Si (Silicon) - Palik")
        mode.setnamed(getattr(p, "name", "polygon"), "vertices", _verts(dy))
        mode.addeme(x=L_TOT / 2, y=dy / 2, z=0.11e-6, y_span=dy + 6e-6, z_span=2e-6)
        mode.setnamed("EME", "number of modes for all cell groups", modes)
        mode.setnamed("EME", "number of cell groups", 1)
        mode.setnamed("EME", "group spans", np.array([[L_TOT]]))
        mode.setnamed("EME", "cells", np.array([[cells]]))
        mode.setnamed("EME", "x", L_TOT / 2)
        mode.save(os.path.join(PROJ, "dy%gnm_m%d.lms" % (round(dy * 1e9), modes)))
        mode.select("EME")
        mode.run()
        rec = {"dy_um": dy * 1e6, "cell_um": cell * 1e6, "modes": modes}
        try:
            mode.emepropagate()
            got = mode.getresult("EME", "user s matrix")
            arr = np.array(got["S"]) if (hasattr(got, "keys") and "S" in got.keys()) else np.array(got)
            a2 = np.abs(arr) ** 2
            rec["S_shape"] = list(a2.shape)
            rec["colsum"] = np.round(a2.sum(axis=0), 6).tolist()
            rec["diag"] = np.round(np.diag(a2), 6).tolist()
        except Exception as exc:  # noqa: BLE001
            rec["error"] = str(exc).splitlines()[0][:100]
        out.append(rec)
    return out
