# -*- coding: utf-8 -*-
"""probe_taper.py — does Lumerical EME work at all when the cross-section changes?

The S-bend collapses (~1 %) but the straight control is exactly 1.0. Two things differ from a
straight guide: (i) the cross-section WIDTH could change, (ii) the mode's transverse POSITION
moves. This probe separates them:

  A) gentle width taper 500 -> 600 nm over the middle 100 um, guide CENTRED  -> cross-section
     changes but the mode stays put. Expect colsum ~ 1 if EME handles a varying cross-section.
  B) straight guide at a CONSTANT lateral offset 5 um, window sized to cover it -> the mode sits
     off-centre but does not move. Expect colsum ~ 1 if window position is irrelevant.

If A and B are ~1 but the S-bend is ~1 %, the collapse is specifically the lateral MOVEMENT.
Run through the persistent MODE process (whole-file exec; the channel splits indented blocks).
"""
from __future__ import annotations

import numpy as np

LAM = 1.55e-6
L_TOT = 200e-6
L_BEND = 100e-6
L_STRAIGHT = 50e-6
T_SI = 0.22e-6
SAVE = r"C:\Users\55093\.cline\data\workspaces\chat\PERSONAL_BRAND\BUILDS\min_sbend_eme"


def _scene(mode, win_center: float, win_span: float) -> None:
    mode.switchtolayout()
    mode.deleteall()
    mode.addrect(x=L_TOT / 2, y=win_center, z=-0.5e-6, x_span=L_TOT, y_span=win_span,
                 z_span=1e-6, material="SiO2 (Glass) - Palik")
    mode.addeme(x=L_TOT / 2, y=win_center, z=0.11e-6, y_span=win_span, z_span=2e-6)
    mode.setnamed("EME", "number of modes for all cell groups", 8)
    mode.setnamed("EME", "number of cell groups", 1)
    mode.setnamed("EME", "group spans", np.array([[L_TOT]]))
    mode.setnamed("EME", "cells", np.array([[40]]))
    mode.setnamed("EME", "x", L_TOT / 2)


def _poly(mode, verts) -> None:
    p = mode.addpoly(x=0, y=0, z=T_SI / 2, z_span=T_SI, material="Si (Silicon) - Palik")
    mode.setnamed(getattr(p, "name", "polygon"), "vertices", np.asarray(verts))


def verts_taper(w0: float = 0.5e-6, w1: float = 0.6e-6, n: int = 401) -> np.ndarray:
    x = np.linspace(0.0, L_TOT, n)
    w = np.full_like(x, w0)
    m = (x >= L_STRAIGHT) & (x <= L_STRAIGHT + L_BEND)
    w[m] = w0 + (w1 - w0) * (x[m] - L_STRAIGHT) / L_BEND
    w[x > L_STRAIGHT + L_BEND] = w1
    top = np.vstack([x, +w / 2]).T
    bot = np.vstack([x, -w / 2]).T
    return np.vstack([top, bot[::-1]])


def _read(mode, rec) -> dict:
    try:
        mode.emepropagate()
        got = mode.getresult("EME", "user s matrix")
        arr = np.array(got["S"]) if (hasattr(got, "keys") and "S" in got.keys()) else np.array(got)
        a2 = np.abs(arr) ** 2
        rec["S_shape"] = list(a2.shape)
        rec["colsum"] = np.round(a2.sum(axis=0), 6).tolist()
    except Exception as exc:  # noqa: BLE001
        rec["error"] = str(exc).splitlines()[0][:80]
    return rec


def run(mode, taper_w1: float = 0.6e-6) -> dict:
    out = {}
    # A) width taper, guide centred at y = 0, 6 um window
    _scene(mode, 0.0, 6e-6)
    _poly(mode, verts_taper(0.5e-6, taper_w1))
    mode.save(SAVE + r"\probe_taperA.lms")
    mode.select("EME")
    mode.run()
    out["A_taper"] = _read(mode, {"w0_nm": 500, "w1_nm": round(taper_w1 * 1e9)})
    # B) straight guide, CONSTANT 5 um offset, 11 um window centred at 2.5 um
    _scene(mode, 2.5e-6, 11e-6)
    mode.addrect(x=L_TOT / 2, y=5e-6, z=T_SI / 2, x_span=L_TOT, y_span=0.5e-6, z_span=T_SI,
                 material="Si (Silicon) - Palik")
    mode.save(SAVE + r"\probe_taperB.lms")
    mode.select("EME")
    mode.run()
    out["B_constant_offset"] = _read(mode, {"offset_um": 5.0, "window_span_um": 11.0})
    return out
