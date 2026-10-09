# -*- coding: utf-8 -*-
"""probe_props.py — which mesh / mode properties does the EME object accept?

Purpose: the minimal-S-bend probe left the transverse mesh fixed at 1 x 52 x 52 ("Refined 0
mesh cells") while the column-sum stayed erratic (~0.3-5 %) for every mode count. Before
concluding, find out whether a mesh-resolution knob exists whose change actually moves the
engine gridpoints. Read-only against the object; builds its own throwaway scene.

Run through the persistent MODE process (execute_python_code) because a standalone python
cannot load the lumapi interop DLL (WinError 14001).
"""
from __future__ import annotations

import numpy as np


def run(mode) -> dict:
    mode.switchtolayout()
    mode.deleteall()
    mode.addrect(x=100e-6, y=0, z=-0.5e-6, x_span=200e-6, y_span=11e-6, z_span=1e-6,
                 material="SiO2 (Glass) - Palik")
    mode.addrect(x=100e-6, y=0, z=0.11e-6, x_span=200e-6, y_span=0.5e-6, z_span=0.22e-6,
                 material="Si (Silicon) - Palik")
    mode.addeme(x=100e-6, y=0, z=0.11e-6, y_span=11e-6, z_span=2e-6)
    mode.setnamed("EME", "number of modes for all cell groups", 8)
    props = ["mesh cells per wavelength", "mesh accuracy", "mesh", "mode mesh",
             "cells per wavelength", "number of mesh cells", "mesh cells", "refinement",
             "mesh size", "override global mesh", "meshing", "mesh type", "dx", "dy", "dz",
             "x span", "y span", "z span", "number of modes for all cell groups",
             "group spans", "cells", "number of cell groups",
             "allow custom eigensolver settings", "number of trial modes",
             "use fully vectorial", "bend radius", "propagation axis", "solver type"]
    out = {}
    for p in props:
        try:
            v = mode.getnamed("EME", p)
            out[p] = "%s=%s" % (type(v).__name__, np.array(v).ravel()[:4].tolist())
        except Exception as exc:  # noqa: BLE001
            out[p] = "FAIL:" + str(exc).splitlines()[0][:50]
    return out
