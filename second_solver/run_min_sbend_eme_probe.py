# -*- coding: utf-8 -*-
"""run_min_sbend_eme_probe.py — diagnose WHY the minimal S-bend column-sum collapses.

WHY THIS FILE EXISTS
--------------------
run_min_sbend_eme.py showed a straight control at column-sum = 1.0 but the S-bend at ~1 %,
and that ~1 % did not move when the cell length was refined (5 / 2.5 / 1 um -> 0.90 / 1.16 /
1.15 %). The readings are written into a 2x2 user S-matrix whose off-diagonal and diagonal are
BOTH tiny, i.e. ~99 % of the power is neither transmitted nor reflected: it leaves the mode
basis. The engine log shows the transverse mesh as only 1 x 52 x 52 over an 11 um window.

JUDGMENT FIRST (2026-10-07 next session)
----------------------------------------
Hypothesis H1: the ~1 % is a TRUNCATED EME MODE BASIS (2 modes) on a laterally shifted
high-contrast waveguide inside a wide window, not the cell length.
  * Test: raise the number of modes at FIXED cell length. Column-sum climbing toward 1
    supports H1; a flat ~1 % rejects it.
  * Control: the straight case (dy = 0) must keep column-sum = 1.0 at every mode count.
Counter-evidence (H1 rejected) if the bend column-sum stays ~1 % at high mode count.

Deliberately NOT tested here: "continuous curve vs piecewise staircase". EME takes the
cross-section at each cell, so a curve and a staircase that share the same cell centres carry
the same cross-sections; that experiment is expected to be a no-op and is deferred.

Outputs (this folder): probe.log, probe_results.json, probe_projects/*.lms
"""
from __future__ import annotations

import json
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "probe.log")
PROJ_DIR = os.path.join(HERE, "probe_projects")

LAM = 1.55e-6
W = 0.50e-6
T_SI = 0.22e-6
L_BEND = 100e-6
L_STRAIGHT = 50e-6
L_TOT = 2 * L_STRAIGHT + L_BEND
MAT_SI = "Si (Silicon) - Palik"
MAT_SIO2 = "SiO2 (Glass) - Palik"


def log(msg: str) -> None:
    line = "%s  %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def strip_vertices(dy: float, n: int = 401) -> np.ndarray:
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


def build(mode, dy: float, modes: int) -> None:
    mode.switchtolayout()
    mode.deleteall()
    mode.addrect(x=L_TOT / 2, y=dy / 2, z=-0.5e-6, x_span=L_TOT, y_span=dy + 6e-6,
                 z_span=1e-6, material=MAT_SIO2)
    verts = strip_vertices(dy)
    si = mode.addpoly(x=0, y=0, z=T_SI / 2, z_span=T_SI, material=MAT_SI)
    name = getattr(si, "name", "polygon")
    mode.setnamed(name, "vertices", verts)
    mode.addeme(x=L_TOT / 2, y=dy / 2, z=0.11e-6, y_span=dy + 6e-6, z_span=2e-6)
    mode.setnamed("EME", "number of modes for all cell groups", modes)
    mode.setnamed("EME", "number of cell groups", 1)
    mode.setnamed("EME", "group spans", np.array([[L_TOT]]))
    mode.setnamed("EME", "cells", np.array([[int(round(L_TOT / 5e-6))]]))
    mode.setnamed("EME", "x", L_TOT / 2)
    log("build dy=%.1f um: modes=%d, x span=%.3f um, centre=%.3f um, y span=%.3f um"
        % (dy * 1e6, int(mode.getnamed("EME", "number of modes for all cell groups")),
           float(mode.getnamed("EME", "x span")) * 1e6, float(mode.getnamed("EME", "x")) * 1e6,
           float(mode.getnamed("EME", "y span")) * 1e6))


def point(mode, dy: float, modes: int, cell_um: float) -> dict:
    cells = int(round(L_TOT / (cell_um * 1e-6)))
    mode.switchtolayout()
    mode.setnamed("EME", "number of modes for all cell groups", modes)
    mode.setnamed("EME", "number of cell groups", 1)
    mode.setnamed("EME", "group spans", np.array([[L_TOT]]))
    mode.setnamed("EME", "cells", np.array([[cells]]))
    mode.setnamed("EME", "x", L_TOT / 2)
    if not os.path.isdir(PROJ_DIR):
        os.makedirs(PROJ_DIR)
    project = os.path.join(PROJ_DIR, "probe_dy%g_m%d_c%gum.lms" % (dy * 1e6, modes, cell_um))
    mode.save(project)
    log("--- point dy=%.1f um modes=%d cell=%.2f um (%d cells) ---"
        % (dy * 1e6, modes, cell_um, cells))
    mode.select("EME")
    mode.run()
    rec = {"dy_um": dy * 1e6, "modes": modes, "cell_um": cell_um, "cells": cells}
    try:
        mode.emepropagate()
        rec["propagate_ok"] = True
    except Exception as exc:  # noqa: BLE001
        rec["propagate_ok"] = False
        rec["error"] = str(exc).splitlines()[0][:120]
        log("propagate refused: %s" % rec["error"])
        return rec
    got = None
    for prov, rname in (("EME", "user s matrix"), ("EME", "power normalized user s matrix"),
                        ("EME", "S")):
        try:
            got = mode.getresult(prov, rname)
            rec["provider"] = prov
            rec["result_name"] = rname
            break
        except Exception:  # noqa: BLE001
            pass
    try:
        if hasattr(got, "keys") and "S" in got.keys():
            arr = np.array(got["S"])
        else:
            arr = np.array(got)
        a2 = np.abs(arr) ** 2
        rec["S_shape"] = list(a2.shape)
        rec["colsum"] = np.round(a2.sum(axis=0), 6).tolist()
        rec["diag"] = np.round(np.diag(a2), 6).tolist()
        log("S shape=%s diag=%s colsum=%s" % (rec["S_shape"], rec["diag"], rec["colsum"]))
    except Exception as exc:  # noqa: BLE001
        rec["read_error"] = str(exc).splitlines()[0][:120]
        log("read error: %s" % rec["read_error"])
    return rec


def main() -> int:
    mode = globals().get("_REUSE_HANDLE")
    if mode is None:
        import lumapi
        mode = lumapi.MODE(hide=True)
    out = {"structure": {"L_tot_um": L_TOT * 1e6, "w_um": W * 1e6, "t_si_um": T_SI * 1e6,
                         "lam_um": LAM * 1e6,
                         "materials": "Lumerical built-in Palik Si / SiO2 (declared substitution)"},
           "hypothesis": "H1: ~1% column-sum is a truncated EME mode basis, not cell length",
           "points": []}
    # (dy_m, modes, cell_um): straight control + a mode-count sweep at fixed 5 um cells
    configs = [(0.0, 2, 5.0), (0.0, 24, 5.0),
               (5.0e-6, 2, 5.0), (5.0e-6, 4, 5.0), (5.0e-6, 8, 5.0), (5.0e-6, 16, 5.0),
               (5.0e-6, 24, 5.0), (5.0e-6, 32, 5.0), (5.0e-6, 48, 5.0)]
    for dy, modes, cell in configs:
        build(mode, dy, modes)
        out["points"].append(point(mode, dy, modes, cell))
        with open(os.path.join(HERE, "probe_results.json"), "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2)
    log("wrote probe_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
