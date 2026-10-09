# -*- coding: utf-8 -*-
"""probe_ports.py — discover the EME port API on this install.

Motivation (PROBE_FINDINGS_20261007.md): without explicit port objects the "user s matrix" is
2x2, i.e. one mode per port, and a previous round recorded that adding addemeport objects turned
it into 4x4 with the column-sum rising to ~17 %. So the port mode count is the leading suspect.
This file discovers what addemeport() returns and which names select, on a throwaway straight
scene. Run through the persistent MODE process.
"""
from __future__ import annotations

import os

import numpy as np

L_TOT = 200e-6


def base(mode, dy: float = 0.0, modes: int = 8, cells: int = 40) -> None:
    mode.switchtolayout()
    mode.deleteall()
    mode.addrect(x=L_TOT / 2, y=dy / 2, z=-0.5e-6, x_span=L_TOT, y_span=dy + 6e-6,
                 z_span=1e-6, material="SiO2 (Glass) - Palik")
    mode.addrect(x=L_TOT / 2, y=dy / 2, z=0.11e-6, x_span=L_TOT, y_span=0.5e-6,
                 z_span=0.22e-6, material="Si (Silicon) - Palik")
    mode.addeme(x=L_TOT / 2, y=dy / 2, z=0.11e-6, y_span=dy + 6e-6, z_span=2e-6)
    mode.setnamed("EME", "number of modes for all cell groups", modes)
    mode.setnamed("EME", "number of cell groups", 1)
    mode.setnamed("EME", "group spans", np.array([[L_TOT]]))
    mode.setnamed("EME", "cells", np.array([[cells]]))
    mode.setnamed("EME", "x", L_TOT / 2)


def discover(mode) -> dict:
    base(mode)
    rec = {}
    for label, fn in (("addemeport()", lambda: mode.addemeport()),
                      ("addemeport(x=0)", lambda: mode.addemeport(x=0.0)),
                      ("addemeport(location left)", lambda: mode.addemeport("left"))):
        try:
            h = fn()
            rec[label] = "OK type=%s name=%s str=%s" % (
                type(h).__name__, str(getattr(h, "name", "?")), str(h)[:60])
        except Exception as exc:  # noqa: BLE001
            rec[label] = "FAIL: " + str(exc).splitlines()[0][:90]
    # which names can be selected now?
    for cand in ("port_1", "port_2", "EME port", "EME_port_1", "EME Port 1",
                 "EME::port_1", "EME port 1", "::model::EME port"):
        try:
            mode.eval('select("%s");' % cand)
            rec["select:" + cand] = "OK x=%s" % (mode.get("x"),)
        except Exception as exc:  # noqa: BLE001
            rec["select:" + cand] = "FAIL"
    # the raw script listing
    try:
        rec["script_get_object_count"] = int(mode.getnamednumber("EME", "number of cell groups"))
    except Exception as exc:  # noqa: BLE001
        rec["script_get_object_count"] = "FAIL:" + str(exc)[:40]
    return rec


def port_probe(mode) -> dict:
    base(mode)
    h1 = mode.addemeport()
    h2 = mode.addemeport()
    rec = {"h1_name": str(h1.name), "h2_name": str(h2.name)}
    rec["h1_methods"] = [m for m in dir(h1) if not m.startswith("_")][:30]
    for prop in ("x", "y", "z", "y span", "z span", "number of modes",
                 "mode selection", "number of trial modes"):
        try:
            v = h1.get(prop)
            rec["h1.get:" + prop] = str(np.array(v).ravel()[:3].tolist())
        except Exception as exc:  # noqa: BLE001
            rec["h1.get:" + prop] = "FAIL:" + str(exc).splitlines()[0][:45]
    return rec


def port_set(mode) -> dict:
    base(mode)
    h1 = mode.addemeport()
    h2 = mode.addemeport()
    rec = {}
    try:
        rec["x_read"] = float(h1.x)
    except Exception as exc:  # noqa: BLE001
        rec["x_read"] = "FAIL:" + str(exc)[:50]
    try:
        h1.x = 0.0
        rec["x_write"] = "OK read_back=%s" % (float(h1.x),)
    except Exception as exc:  # noqa: BLE001
        rec["x_write"] = "FAIL:" + str(exc)[:50]
    for prop in ("name", "type", "mode selection", "selected mode numbers",
                 "port location", "use full simulation span", "y span", "z span"):
        try:
            rec["getattr:" + prop] = str(getattr(h1, prop))
        except Exception as exc:  # noqa: BLE001
            rec["getattr:" + prop] = "FAIL:" + str(exc)[:45]
    return rec


def port_names(mode) -> dict:
    """Safe: read only the auto name (attribute .name), then try full-path addressing.
    Do NOT touch numeric SimObject attributes -- that wedged the process on 2026-10-07."""
    base(mode)
    h1 = mode.addemeport()
    name = str(getattr(h1, "name", "?"))
    rec = {"auto_name": name}
    for full in (name, "::model::" + name, "EME::" + name, "model::" + name,
                 "::root::" + name):
        try:
            rec["getnamed:x@" + full] = float(mode.getnamed(full, "x"))
        except Exception as exc:  # noqa: BLE001
            rec["getnamed:x@" + full] = "FAIL:" + str(exc).splitlines()[0][:40]
    for prop in ("mode selection", "selected mode numbers", "port location",
                 "use full simulation span"):
        try:
            rec["EME|" + prop] = str(np.array(mode.getnamed("EME", prop)).ravel()[:4].tolist())
        except Exception as exc:  # noqa: BLE001
            rec["EME|" + prop] = "FAIL:" + str(exc).splitlines()[0][:40]
    return rec


L_BEND = 100e-6
L_STRAIGHT = 50e-6
W = 0.5e-6
T_SI = 0.22e-6
SAVE = os.path.dirname(os.path.abspath(__file__))


def _verts(dy: float, n: int = 401) -> np.ndarray:
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


def bend_run(mode, add_ports: bool = False, dy: float = 5.0e-6, modes: int = 8,
             cells: int = 40) -> dict:
    mode.switchtolayout()
    mode.deleteall()
    mode.addrect(x=L_TOT / 2, y=dy / 2, z=-0.5e-6, x_span=L_TOT, y_span=dy + 6e-6,
                 z_span=1e-6, material="SiO2 (Glass) - Palik")
    p = mode.addpoly(x=0, y=0, z=T_SI / 2, z_span=T_SI, material="Si (Silicon) - Palik")
    mode.setnamed(getattr(p, "name", "polygon"), "vertices", _verts(dy))
    mode.addeme(x=L_TOT / 2, y=dy / 2, z=0.11e-6, y_span=dy + 6e-6, z_span=2e-6)
    mode.setnamed("EME", "number of modes for all cell groups", modes)
    mode.setnamed("EME", "number of cell groups", 1)
    mode.setnamed("EME", "group spans", np.array([[L_TOT]]))
    mode.setnamed("EME", "cells", np.array([[cells]]))
    mode.setnamed("EME", "x", L_TOT / 2)
    rec = {"add_ports": add_ports}
    if add_ports:
        n = 0
        for xpos in (0.0, L_TOT):
            try:
                mode.addemeport(x=xpos)
                n += 1
            except Exception as exc:  # noqa: BLE001
                rec["add_port_fail_%s" % xpos] = str(exc)[:40]
        rec["ports_added"] = n
    mode.save(SAVE + r"\probe_bend_ports_%s.lms" % ("on" if add_ports else "off"))
    mode.select("EME")
    mode.run()
    try:
        mode.emepropagate()
        got = mode.getresult("EME", "user s matrix")
        arr = np.array(got["S"]) if (hasattr(got, "keys") and "S" in got.keys()) else np.array(got)
        a2 = np.abs(arr) ** 2
        rec["S_shape"] = list(a2.shape)
        rec["colsum"] = np.round(a2.sum(axis=0), 6).tolist()
        rec["diag"] = np.round(np.diag(a2), 6).tolist()
    except Exception as exc:  # noqa: BLE001
        rec["error"] = str(exc).splitlines()[0][:80]
    return rec
