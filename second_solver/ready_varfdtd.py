# -*- coding: utf-8 -*-
"""ready_varfdtd.py — build and SAVE the varFDTD minimal-S-bend project, WITHOUT running it.

Purpose: leave a ready-to-run project in the visible GUI so you can set the parallel-task count
(Resources) to <= 4, then press Run. Mirrors probe_varfdtd.py minus the run().
"""
from __future__ import annotations

import os

import numpy as np

L_TOT = 200e-6
L_BEND = 100e-6
L_STRAIGHT = 50e-6
W = 0.5e-6
T_SI = 0.22e-6
SAVE_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "ready_sbend_varfdtd.lms")


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


def _named(handle, default: str) -> str:
    return str(getattr(handle, "name", default))


def build(mode, dy: float = 5.0e-6, save_path: str = SAVE_DEFAULT,
          straight: bool = False) -> dict:
    mode.switchtolayout()
    mode.deleteall()
    mode.addrect(x=L_TOT / 2, y=dy / 2, z=-0.5e-6, x_span=L_TOT, y_span=dy + 6e-6,
                 z_span=1e-6, material="SiO2 (Glass) - Palik")
    if straight:
        mode.addrect(x=L_TOT / 2, y=0.0, z=T_SI / 2, x_span=L_TOT, y_span=W, z_span=T_SI,
                     material="Si (Silicon) - Palik")
    else:
        p = mode.addpoly(x=0, y=0, z=T_SI / 2, z_span=T_SI, material="Si (Silicon) - Palik")
        mode.setnamed(getattr(p, "name", "polygon"), "vertices", verts(dy))
    h = mode.addvarfdtd()
    vn = _named(h, "varFDTD")
    for prop, val in (("x", L_TOT / 2), ("y", dy / 2), ("z", T_SI / 2),
                      ("x span", L_TOT + 8e-6), ("y span", dy + 6e-6), ("z span", 2e-6),
                      ("simulation time", 3000e-15)):
        try:
            mode.setnamed(vn, prop, val)
        except Exception:  # noqa: BLE001
            pass
    y0 = 0.0 if straight else dy / 2
    hs = mode.addmodesource()
    sn = _named(hs, "source")
    for prop, val in (("injection axis", "x"), ("direction", "Forward"), ("x", 3e-6),
                      ("y", y0), ("y span", dy + 6e-6),
                      ("wavelength start", 1.5e-6), ("wavelength stop", 1.6e-6)):
        try:
            mode.setnamed(sn, prop, val)
        except Exception:  # noqa: BLE001
            pass
    hp = mode.addpower()
    pn = _named(hp, "monitor")
    for prop, val in (("monitor type", "2D X-normal"), ("x", L_TOT - 3e-6),
                      ("y", y0), ("y span", dy + 6e-6)):
        try:
            mode.setnamed(pn, prop, val)
        except Exception:  # noqa: BLE001
            pass
    mode.save(save_path)
    return {"saved": save_path, "solver": vn, "source": sn, "monitor": pn}
