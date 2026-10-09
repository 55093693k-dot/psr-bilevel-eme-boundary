# -*- coding: utf-8 -*-
"""probe_mesh2.py — can the EME mode mesh be made finer, and does that fix the S-bend?

KEY RESULT already established (probe_taper.py): a width taper gives colsum 0.999 and a straight
guide at a CONSTANT 5 um offset gives 1.000, so EME handles changing cross-sections and offsets
fine; only the LATERAL MOVEMENT of the S-bend collapses (~0.055). This probe tests whether a finer
transverse (mode-solver) grid -- enabled via "allow custom eigensolver settings" then dx/dy/dz --
recovers it.
"""
from __future__ import annotations

import os

import numpy as np

L_TOT = 200e-6
L_BEND = 100e-6
L_STRAIGHT = 50e-6
W = 0.5e-6
T_SI = 0.22e-6
SAVE = os.path.dirname(os.path.abspath(__file__))


def verts(dy: float, n: int = 401) -> np.ndarray:
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


def _build(mode, dy: float = 5e-6, modes: int = 8, cells: int = 40) -> None:
    mode.switchtolayout()
    mode.deleteall()
    mode.addrect(x=L_TOT / 2, y=dy / 2, z=-0.5e-6, x_span=L_TOT, y_span=dy + 6e-6,
                 z_span=1e-6, material="SiO2 (Glass) - Palik")
    p = mode.addpoly(x=0, y=0, z=T_SI / 2, z_span=T_SI, material="Si (Silicon) - Palik")
    mode.setnamed(getattr(p, "name", "polygon"), "vertices", verts(dy))
    mode.addeme(x=L_TOT / 2, y=dy / 2, z=0.11e-6, y_span=dy + 6e-6, z_span=2e-6)
    mode.setnamed("EME", "number of modes for all cell groups", modes)
    mode.setnamed("EME", "number of cell groups", 1)
    mode.setnamed("EME", "group spans", np.array([[L_TOT]]))
    mode.setnamed("EME", "cells", np.array([[cells]]))
    mode.setnamed("EME", "x", L_TOT / 2)


def _try(mode, prop: str, val, rec: dict, tag: str) -> None:
    try:
        mode.setnamed("EME", prop, val)
        rec[tag] = "OK"
    except Exception as exc:  # noqa: BLE001
        rec[tag] = "FAIL:" + str(exc).splitlines()[0][:45]


def run(mode, mesh_nm=(10.0, 20.0)) -> dict:
    out = {}
    for mnm in (None,) + tuple(mesh_nm):
        _build(mode)
        rec = {"mesh_nm": mnm}
        if mnm is not None:
            _try(mode, "allow custom eigensolver settings", 1, rec, "flag")
            my = mnm * 1e-9
            _try(mode, "dx", my, rec, "set_dx")
            _try(mode, "dy", my, rec, "set_dy")
            _try(mode, "dz", my, rec, "set_dz")
        mode.save(SAVE + r"\probe_m%s.lms" % ("base" if mnm is None else str(mnm)))
        mode.select("EME")
        mode.run()
        try:
            mode.emepropagate()
            got = mode.getresult("EME", "user s matrix")
            arr = np.array(got["S"]) if (hasattr(got, "keys") and "S" in got.keys()) else np.array(got)
            a2 = np.abs(arr) ** 2
            rec["colsum"] = np.round(a2.sum(axis=0), 6).tolist()
        except Exception as exc:  # noqa: BLE001
            rec["error"] = str(exc).splitlines()[0][:70]
        out[("baseline" if mnm is None else "mesh%gnm" % mnm)] = rec
    return out


def groups_run(mode, dy: float = 5e-6, modes: int = 8) -> dict:
    """Same S-bend, but split into 3 cell groups (straight|bend|straight) vs one big group."""
    out = {}
    for ng in (1, 3):
        mode.switchtolayout()
        mode.deleteall()
        mode.addrect(x=L_TOT / 2, y=dy / 2, z=-0.5e-6, x_span=L_TOT, y_span=dy + 6e-6,
                     z_span=1e-6, material="SiO2 (Glass) - Palik")
        p = mode.addpoly(x=0, y=0, z=T_SI / 2, z_span=T_SI, material="Si (Silicon) - Palik")
        mode.setnamed(getattr(p, "name", "polygon"), "vertices", verts(dy))
        mode.addeme(x=L_TOT / 2, y=dy / 2, z=0.11e-6, y_span=dy + 6e-6, z_span=2e-6)
        mode.setnamed("EME", "number of modes for all cell groups", modes)
        if ng == 1:
            spans = np.array([[L_TOT]])
            cells = np.array([[40]])
        else:
            spans = np.array([[50e-6], [100e-6], [50e-6]])
            cells = np.array([[10], [20], [10]])
        mode.setnamed("EME", "number of cell groups", ng)
        mode.setnamed("EME", "group spans", spans)
        mode.setnamed("EME", "cells", cells)
        mode.setnamed("EME", "x", L_TOT / 2)
        mode.save(SAVE + r"\probe_g%d.lms" % ng)
        mode.select("EME")
        mode.run()
        rec = {"ngroups": ng}
        try:
            mode.emepropagate()
            got = mode.getresult("EME", "user s matrix")
            arr = np.array(got["S"]) if (hasattr(got, "keys") and "S" in got.keys()) else np.array(got)
            a2 = np.abs(arr) ** 2
            rec["S_shape"] = list(a2.shape)
            rec["colsum"] = np.round(a2.sum(axis=0), 6).tolist()
        except Exception as exc:  # noqa: BLE001
            rec["error"] = str(exc).splitlines()[0][:70]
        out["groups%d" % ng] = rec
    return out
