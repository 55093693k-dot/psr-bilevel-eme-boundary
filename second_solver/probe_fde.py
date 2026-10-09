# -*- coding: utf-8 -*-
"""probe_fde.py — sanity-check the SOI cross-section.

Solve the straight strip's cross-sectional modes and report neff. A fundamental TE-like neff
near ~2.4 for a 500 x 220 nm Si strip on SiO2 validates materials + mesh + geometry in one shot;
anything far off (e.g. ~1.45) means the model layer is wrong. Run through the persistent MODE
process.
"""
from __future__ import annotations

import os

import numpy as np

LAM = 1.55e-6
HERE = os.path.dirname(os.path.abspath(__file__))


def run(mode, solver_type: str = "2D X normal", y_span: float = 4e-6, trial: int = 4) -> dict:
    mode.switchtolayout()
    mode.deleteall()
    mode.addrect(x=100e-6, y=0, z=-0.5e-6, x_span=200e-6, y_span=6e-6, z_span=1e-6,
                 material="SiO2 (Glass) - Palik")
    mode.addrect(x=100e-6, y=0, z=0.11e-6, x_span=200e-6, y_span=0.5e-6, z_span=0.22e-6,
                 material="Si (Silicon) - Palik")
    mode.addfde()
    mode.setnamed("FDE", "solver type", solver_type)
    mode.setnamed("FDE", "wavelength", LAM)
    mode.setnamed("FDE", "x", 100e-6)
    mode.setnamed("FDE", "y", 0.0)
    mode.setnamed("FDE", "z", 0.11e-6)
    mode.setnamed("FDE", "y span", y_span)
    mode.setnamed("FDE", "z span", 2e-6)
    mode.setnamed("FDE", "number of trial modes", trial)
    mode.save(os.path.join(HERE, "probe_fde.lms"))
    n = mode.findmodes()
    out = {"solver_type": solver_type, "y_span_um": y_span * 1e6, "num_modes": int(n)}
    for i in range(1, min(int(n), 4) + 1):
        for field in ("neff", "TE polarization fraction"):
            try:
                v = np.array(mode.getdata("FDE::data::mode%d" % i, field)).ravel()
                out["mode%d|%s" % (i, field)] = float(v[0])
            except Exception as exc:  # noqa: BLE001
                out["mode%d|%s" % (i, field)] = "FAIL:" + str(exc).splitlines()[0][:40]
    return out
