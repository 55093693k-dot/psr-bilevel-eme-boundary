# -*- coding: utf-8 -*-
"""probe_bentfde.py — third-method check: is the S-bend lossless?

The S-bend (offset 5 um over 100 um) has a minimum radius of curvature
R = L_BEND / (pi * DY) ~ 405 um. Solve the FDE mode of a BENT waveguide at a few radii and read
the loss. Expectation: ~0 at 405 um, and a finite loss only at much tighter radii (a sanity check
that the bent solver actually works). If 405 um is ~0, the S-bend is lossless and the EME collapse
(~5 %) is a modelling artifact, not device loss.
"""
from __future__ import annotations

import numpy as np

LAM = 1.55e-6
W = 0.5e-6
T_SI = 0.22e-6
SAVE = r"C:\Users\55093\.cline\data\workspaces\chat\PERSONAL_BRAND\BUILDS\min_sbend_eme"


def run(mode, radii_um=(405.0, 10.0, 5.0)) -> dict:
    out = {}
    for r_um in radii_um:
        mode.switchtolayout()
        mode.deleteall()
        mode.addrect(x=0, y=0, z=-0.5e-6, x_span=4e-6, y_span=8e-6, z_span=1e-6,
                     material="SiO2 (Glass) - Palik")
        mode.addrect(x=0, y=0, z=T_SI / 2, x_span=4e-6, y_span=W, z_span=T_SI,
                     material="Si (Silicon) - Palik")
        mode.addfde()
        mode.setnamed("FDE", "solver type", "2D X normal")
        mode.setnamed("FDE", "wavelength", LAM)
        mode.setnamed("FDE", "x", 0.0)
        mode.setnamed("FDE", "y", 0.0)
        mode.setnamed("FDE", "z", T_SI / 2)
        mode.setnamed("FDE", "y span", 8e-6)
        mode.setnamed("FDE", "z span", 2e-6)
        mode.setnamed("FDE", "number of trial modes", 4)
        rec = {"radius_um": r_um}
        for prop, val in (("y min bc", "PML"), ("y max bc", "PML"),
                          ("bent waveguide", 1), ("bend radius", r_um * 1e-6)):
            try:
                mode.setnamed("FDE", prop, val)
                rec[prop] = "OK"
            except Exception as exc:  # noqa: BLE001
                rec[prop] = "FAIL:" + str(exc).splitlines()[0][:40]
        mode.save(SAVE + r"\probe_bentfde_%gum.lms" % r_um)
        n = mode.findmodes()
        rec["num_modes"] = int(n)
        for i in (1, 2):
            for f in ("neff", "loss", "TE polarization fraction"):
                try:
                    rec["m%d|%s" % (i, f)] = float(np.array(mode.getdata("FDE::data::mode%d" % i, f)).ravel()[0])
                except Exception as exc:  # noqa: BLE001
                    rec["m%d|%s" % (i, f)] = "FAIL:" + str(exc).splitlines()[0][:25]
        out["R%gum" % r_um] = rec
    return out
