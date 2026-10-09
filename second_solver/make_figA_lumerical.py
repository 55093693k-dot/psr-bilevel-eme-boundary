# -*- coding: utf-8 -*-
"""make_figA_lumerical.py — export the structure view using Lumerical's OWN export commands.

Lumerical MODE exposes exportview() / exportfigure() (found by dir()); this builds the minimal
S-bend and tries both, saving under figures_pilot/. Run through the persistent MODE process.
"""
from __future__ import annotations

import os

import numpy as np

OUT = os.path.join(r"C:\Users\55093\.cline\data\workspaces\chat\PERSONAL_BRAND\BUILDS\optica_build",
                   "figures_pilot")
L_TOT, L_BEND, L_STR, W, DY, T_SI = 200.0, 100.0, 50.0, 0.5, 5.0, 0.22


def _verts(dy_um: float, n: int = 401) -> np.ndarray:
    x = np.linspace(0.0, L_TOT, n)
    y = np.zeros_like(x)
    inb = (x > L_STR) & (x < L_STR + L_BEND)
    y[inb] = dy_um * (1 - np.cos(np.pi * (x[inb] - L_STR) / L_BEND)) / 2.0
    y[x >= L_STR + L_BEND] = dy_um
    th = np.arctan(np.gradient(y, x))
    nx, ny = -np.sin(th), np.cos(th)
    top = np.vstack([x + nx * W / 2, y + ny * W / 2]).T * 1e-6
    bot = np.vstack([x - nx * W / 2, y - ny * W / 2]).T * 1e-6
    return np.vstack([top, bot[::-1]])


def run(mode) -> dict:
    rec = {}
    mode.switchtolayout()
    mode.deleteall()
    mode.addrect(x=L_TOT / 2 * 1e-6, y=DY / 2 * 1e-6, z=-0.5e-6,
                 x_span=L_TOT * 1e-6, y_span=(DY + 6) * 1e-6, z_span=1e-6,
                 material="SiO2 (Glass) - Palik")
    p = mode.addpoly(x=0, y=0, z=T_SI / 2 * 1e-6, z_span=T_SI * 1e-6,
                     material="Si (Silicon) - Palik")
    mode.setnamed(getattr(p, "name", "polygon"), "vertices", _verts(DY))
    proj = os.path.join(OUT, "lum_min_sbend.lms")
    mode.save(proj)
    rec["saved"] = proj
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    for cmd, fn in (("exportview", lambda: mode.exportview(os.path.join(OUT, "figA_structure_bend_lumerical.png"))),
                    ("exportfigure", lambda: mode.exportfigure(os.path.join(OUT, "figA_structure_bend_lumerical_fig.png")))):
        try:
            fn()
            rec[cmd] = "OK"
        except Exception as exc:  # noqa: BLE001
            rec[cmd] = "FAIL:" + str(exc).splitlines()[0][:70]
    return rec
