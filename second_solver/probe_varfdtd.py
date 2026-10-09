# -*- coding: utf-8 -*-
"""probe_varfdtd.py — independent end-to-end transmission of the S-bend via varFDTD (2.5D).

The EME route collapses; the FDE bent solve says the bend is lossless. varFDTD propagates the
whole 2D effective-index structure and gives a direct transmission, so it is the cleanest third
opinion. This file first DISCOVERS the solver/source/monitor API on this install.

Run through the persistent MODE process (whole-file exec; the channel splits indented blocks).
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


def discover(mode) -> dict:
    rec = {}
    mode.switchtolayout()
    mode.deleteall()
    mode.addrect(x=L_TOT / 2, y=0, z=-0.5e-6, x_span=L_TOT, y_span=6e-6, z_span=1e-6,
                 material="SiO2 (Glass) - Palik")
    mode.addrect(x=L_TOT / 2, y=0, z=T_SI / 2, x_span=L_TOT, y_span=W, z_span=T_SI,
                 material="Si (Silicon) - Palik")
    # add a varFDTD solver (try the common spellings)
    got = None
    for how in ("addvarfdtd()", 'eval addobject("varFDTD")', 'eval addobject("varfdtd")'):
        try:
            if how == "addvarfdtd()":
                mode.addvarfdtd()
            else:
                mode.eval(how.split(" ", 1)[1].strip() + ";")
            rec["add:" + how] = "OK"
            got = how
            break
        except Exception as exc:  # noqa: BLE001
            rec["add:" + how] = "FAIL:" + str(exc).splitlines()[0][:55]
    # probe the solver object name for a few properties
    for name in ("varFDTD", "varfdtd", "FDTD"):
        for prop in ("x span", "y span", "z span"):
            try:
                rec["%s|%s" % (name, prop)] = float(mode.getnamed(name, prop))
            except Exception as exc:  # noqa: BLE001
                rec["%s|%s" % (name, prop)] = "FAIL"
    # probe a mode source and a power monitor
    for label, fn in (
        ("addmode", lambda: mode.addmode(x=2e-6, y=0, z=T_SI / 2, x_span=0, y_span=6e-6, z_span=2e-6, injection_axis="x")),
        ("addpower", lambda: mode.addpower(x=L_TOT - 2e-6, y=0, z=T_SI / 2, x_span=0, y_span=6e-6, z_span=2e-6)),
    ):
        try:
            fn()
            rec[label] = "OK"
        except Exception as exc:  # noqa: BLE001
            rec[label] = "FAIL:" + str(exc).splitlines()[0][:55]
    return rec


def _named(mode, handle, default: str) -> str:
    return str(getattr(handle, "name", default))


def run(mode, dy: float = 5.0e-6, straight: bool = False) -> dict:
    """End-to-end transmission via varFDTD (2.5D). The mode source is addmodesource()."""
    rec = {"straight": straight}
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
    vn = _named(mode, h, "varFDTD")
    rec["solver"] = vn
    for prop, val in (("x", L_TOT / 2), ("y", dy / 2), ("z", T_SI / 2),
                      ("x span", L_TOT + 8e-6), ("y span", dy + 6e-6), ("z span", 2e-6),
                      ("simulation time", 3000e-15)):
        try:
            mode.setnamed(vn, prop, val)
        except Exception as exc:  # noqa: BLE001
            rec["set:" + prop] = "FAIL:" + str(exc).splitlines()[0][:30]
    hs = mode.addmodesource()
    sn = _named(mode, hs, "source")
    rec["source"] = sn
    y0 = 0.0 if straight else dy / 2
    for prop, val in (("injection axis", "x"), ("direction", "Forward"), ("x", 3e-6),
                      ("y", y0), ("y span", dy + 6e-6),
                      ("wavelength start", 1.5e-6), ("wavelength stop", 1.6e-6)):
        try:
            mode.setnamed(sn, prop, val)
        except Exception as exc:  # noqa: BLE001
            rec["src:" + prop] = "FAIL:" + str(exc).splitlines()[0][:30]
    hp = mode.addpower()
    pn = _named(mode, hp, "monitor")
    rec["monitor"] = pn
    for prop, val in (("monitor type", "2D X-normal"), ("x", L_TOT - 3e-6),
                      ("y", y0), ("y span", dy + 6e-6)):
        try:
            mode.setnamed(pn, prop, val)
        except Exception as exc:  # noqa: BLE001
            rec["mon:" + prop] = "FAIL:" + str(exc).splitlines()[0][:30]
    mode.save(SAVE + r"\probe_vfdtd_%s.lms" % ("straight" if straight else "bend"))
    mode.run()
    for mname in (pn, "monitor", "power"):
        try:
            T = np.real(np.array(mode.getresult(mname, "T")).ravel())
            rec["T"] = float(np.mean(T))
            break
        except Exception as exc:  # noqa: BLE001
            rec["T@" + mname] = "FAIL:" + str(exc).splitlines()[0][:40]
    return rec


def run_both(mode) -> dict:
    return {"straight": run(mode, straight=True), "bend": run(mode, straight=False)}
