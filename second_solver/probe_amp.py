# -*- coding: utf-8 -*-
"""probe_amp.py — amplify the CELL feature (author's 2026-10-07 redefinition of "minimal").

"Minimal" = extract ONE feature and AMPLIFY it, not "make the model small". To test the cell clause,
the structure must make the per-cell lateral jump large: keep the lateral offset dy but shorten the
bend, so each cell boundary displaces the guide by ~dy/(#bend cells). Then sweep the CELL LENGTH: if
the column sum moves with it, the cell clause of Sec. 4.2 is verified on this route.
"""
from __future__ import annotations

import numpy as np

MAT_SI = "Si (Silicon) - Palik"
MAT_SIO2 = "SiO2 (Glass) - Palik"
W = 0.5e-6
T_SI = 0.22e-6
SAVE = r"C:\Users\55093\.cline\data\workspaces\chat\PERSONAL_BRAND\BUILDS\min_sbend_eme"


def verts(dy: float, l_str: float, l_bend: float, n: int = 401) -> np.ndarray:
    L = 2 * l_str + l_bend
    x = np.linspace(0.0, L, n)
    y = np.zeros_like(x)
    inb = (x > l_str) & (x < l_str + l_bend)
    y[inb] = dy * (1 - np.cos(np.pi * (x[inb] - l_str) / l_bend)) / 2.0
    y[x >= l_str + l_bend] = dy
    th = np.arctan(np.gradient(y, x))
    nx, ny = -np.sin(th), np.cos(th)
    top = np.vstack([x + nx * W / 2, y + ny * W / 2]).T
    bot = np.vstack([x - nx * W / 2, y - ny * W / 2]).T
    return np.vstack([top, bot[::-1]])


def _build(mode, dy=5e-6, l_str=20e-6, l_bend=20e-6, modes=8, cells=12):
    L = 2 * l_str + l_bend
    mode.switchtolayout()
    mode.deleteall()
    mode.addrect(x=L / 2, y=dy / 2, z=-0.5e-6, x_span=L, y_span=dy + 6e-6, z_span=1e-6,
                 material=MAT_SIO2)
    p = mode.addpoly(x=0, y=0, z=T_SI / 2, z_span=T_SI, material=MAT_SI)
    mode.setnamed(getattr(p, "name", "polygon"), "vertices", verts(dy, l_str, l_bend))
    mode.addeme(x=L / 2, y=dy / 2, z=0.11e-6, y_span=dy + 6e-6, z_span=2e-6)
    mode.setnamed("EME", "number of modes for all cell groups", modes)
    mode.setnamed("EME", "number of cell groups", 1)
    mode.setnamed("EME", "group spans", np.array([[L]]))
    mode.setnamed("EME", "cells", np.array([[cells]]))
    mode.setnamed("EME", "x", L / 2)
    return L


def sweep(mode, cell_um=(5.0, 2.5, 1.0, 0.5), dy=5e-6, l_str=20e-6, l_bend=20e-6,
          modes=8) -> dict:
    L = 2 * l_str + l_bend
    out = {"dy_um": dy * 1e6, "bend_um": l_bend * 1e6, "straight_um": l_str * 1e6,
           "total_um": L * 1e6, "points": {}}
    for c in cell_um:
        cells = int(round(L / (c * 1e-6)))
        _build(mode, dy=dy, l_str=l_str, l_bend=l_bend, modes=modes, cells=cells)
        mode.save(SAVE + r"\amp_bend%g_cell%g.lms" % (l_bend * 1e6, c))
        mode.select("EME")
        mode.run()
        rec = {"cells": cells}
        try:
            mode.emepropagate()
            got = mode.getresult("EME", "user s matrix")
            arr = np.array(got["S"]) if (hasattr(got, "keys") and "S" in got.keys()) else np.array(got)
            a2 = np.abs(arr) ** 2
            rec["colsum"] = np.round(a2.sum(axis=0), 6).tolist()
        except Exception as exc:  # noqa: BLE001
            rec["error"] = str(exc).splitlines()[0][:60]
        out["points"]["cell%gum" % c] = rec
    return out


def sweep_modes(mode, mode_list=(2, 4, 8, 16, 32), cell_um: float = 1.0, dy=5e-6,
                l_str=20e-6, l_bend=20e-6) -> dict:
    """Basis clause on the AMPLIFIED model: fixed cell length, sweep the mode count."""
    L = 2 * l_str + l_bend
    cells = int(round(L / (cell_um * 1e-6)))
    out = {"cell_um": cell_um, "cells": cells, "dy_um": dy * 1e6, "bend_um": l_bend * 1e6,
           "points": {}}
    for m in mode_list:
        _build(mode, dy=dy, l_str=l_str, l_bend=l_bend, modes=m, cells=cells)
        mode.save(SAVE + r"\ampmodes_m%d.lms" % m)
        mode.select("EME")
        mode.run()
        rec = {"modes": m}
        try:
            mode.emepropagate()
            got = mode.getresult("EME", "user s matrix")
            arr = np.array(got["S"]) if (hasattr(got, "keys") and "S" in got.keys()) else np.array(got)
            a2 = np.abs(arr) ** 2
            rec["colsum"] = np.round(a2.sum(axis=0), 6).tolist()
        except Exception as exc:  # noqa: BLE001
            rec["error"] = str(exc).splitlines()[0][:60]
        out["points"]["modes%d" % m] = rec
    return out
