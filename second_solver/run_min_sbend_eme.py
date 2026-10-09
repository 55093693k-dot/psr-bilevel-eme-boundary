# -*- coding: utf-8 -*-
"""run_min_sbend_eme.py — minimal structure (straight -> one S-bend -> straight) in Lumerical MODE EME.

WHY THIS FILE EXISTS
--------------------
Cross-solver *side check* for the method boundary reported in the first report: an EME
column-sum reading is not a device-level absolute insertion loss when the cell length does not
resolve the structure between two laterally offset ports. The main route is Tidy3D EME; this
file reproduces the same minimal structure in a second solver.

It is a file on purpose. On 2026-10-07 the same model was first driven through short code
snippets, and that cost several rounds to four interface artefacts, not physics:
  * indented blocks arriving as separate chunks (SyntaxError / IndentationError),
  * add* constructors rejecting name= for some objects,
  * group spans / cells requiring matrix payloads,
  * only one EME object per object tree.
A normal script has none of those problems.

MINIMAL STRUCTURE
-----------------
50 um straight + 100 um cosine S-bend (lateral offset 5 um) + 50 um straight = 200 um total.
Si 220 nm thick, 500 nm wide, on SiO2, air top cladding. Material models are Lumerical's
built-in Palik models — a declared substitution for the record's Tidy3D material-library models.
Ports at both ends, x-normal, 2 modes per port, single wavelength 1.55 um.

KNOB AND READ-OUT
-----------------
Cell length along x = 5 / 2.5 / 1 um over the same 200 um (40 / 80 / 200 cells).
Read the |S|^2 matrix. column sum = sum over the output-port modes for a given input mode;
key channel = |S(out mode 0 <- in mode 0)|^2. The Tidy3D route moved its key channel
0.99233 (5 um) -> 0.99840 (1 um); the direction is what this side check is looking at.

KNOWN BLOCKER (licence, not physics)
------------------------------------
The EME solver asked for 8 HPC parallel tasks while the licence grants 4
(`Insufficient FlexNet Publisher (FNP) license count of HPC Parallel ... Feature: anshpc ...
FlexNet Licensing error:-25,147`), the solve aborted, and the project stayed in layout mode
(`emepropagate cannot be used while in layout mode`). The licence/log material lives outside
this folder: **read it, never write to it.** This script writes only inside its own folder, and
for every attempted run it reads back the engine log so the reason is on record.

USAGE
-----
  python run_min_sbend_eme.py                 # all three cell lengths
  python run_min_sbend_eme.py --cell-um 5     # one point
Outputs (all in this folder): results.csv, results.json, run.log
"""
from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "run.log")

# ---- minimal structure (SI units) ----
LAM = 1.55e-6
W = 0.50e-6
T_SI = 0.22e-6
DY = 5.0e-6
L_BEND = 100e-6
L_STRAIGHT = 50e-6
L_TOT = 2 * L_STRAIGHT + L_BEND
MAT_SI = "Si (Silicon) - Palik"
MAT_SIO2 = "SiO2 (Glass) - Palik"
N_MODES = 2


def log(msg: str) -> None:
    line = "%s  %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def strip_vertices(n: int = 401) -> np.ndarray:
    """Outline of the Si strip: straight - cosine S-bend - straight, absolute coordinates."""
    x = np.linspace(0.0, L_TOT, n)
    y = np.zeros_like(x)
    in_bend = (x > L_STRAIGHT) & (x < L_STRAIGHT + L_BEND)
    y[in_bend] = DY * (1 - np.cos(np.pi * (x[in_bend] - L_STRAIGHT) / L_BEND)) / 2.0
    y[x >= L_STRAIGHT + L_BEND] = DY
    th = np.arctan(np.gradient(y, x))
    nx, ny = -np.sin(th), np.cos(th)
    top = np.vstack([x + nx * W / 2, y + ny * W / 2]).T
    bot = np.vstack([x - nx * W / 2, y - ny * W / 2]).T
    return np.vstack([top, bot[::-1]])


def build_geometry(mode):
    """Oxide + Si strip + EME object + two ports. Returns the EME and port handles."""
    mode.switchtolayout()
    mode.deleteall()
    mode.addrect(x=L_TOT / 2, y=DY / 2, z=-0.5e-6, x_span=L_TOT, y_span=DY + 6e-6, z_span=1e-6, material=MAT_SIO2)
    verts = strip_vertices()
    si = mode.addpoly(x=0, y=0, z=T_SI / 2, z_span=T_SI, material=MAT_SI)
    strip_name = getattr(si, "name", "polygon")
    log("polygon auto-name: %s" % strip_name)
    poly_ok = None
    for plabel, payload in (("nested list", verts.tolist()), ("numpy array", verts)):
        try:
            mode.setnamed(strip_name, "vertices", payload)
            poly_ok = "setnamed(%s, vertices) via %s" % (strip_name, plabel)
            break
        except Exception as exc:  # noqa: BLE001
            log("vertices via %-12s FAIL: %s" % (plabel, str(exc).splitlines()[0][:70]))
    log("Si strip: %s (%d vertices)" % (poly_ok, len(verts)))
    if poly_ok is None:
        raise RuntimeError("cannot set the polygon vertices: refusing to measure a wrong geometry")
    mode.addeme(x=L_TOT / 2, y=DY / 2, z=0.11e-6, y_span=DY + 6e-6, z_span=2e-6)
    mode.setnamed("EME", "number of modes for all cell groups", N_MODES)
    # The region must cover the structure from the moment it is built. Ask (2026-10-07, author):
    # "the fdtd area didnt cover the structure" -- the EME had been left at its default 1.89-lambda
    # span, so early runs measured a 2.9 um stub. Set span/cells/centre here, and log the read-back;
    # run_point re-asserts them per point and its read-back is the gate before any run.
    mode.setnamed("EME", "number of cell groups", 1)
    mode.setnamed("EME", "group spans", np.array([[L_TOT]]))
    mode.setnamed("EME", "cells", np.array([[int(round(L_TOT / (5e-6)))]]))
    mode.setnamed("EME", "x", L_TOT / 2)
    log("EME region at build: x span %.3f um, %d cells, centred at %.3f um (structure spans 0..%.1f um)"
        % (float(mode.getnamed("EME", "x span")) * 1e6, int(mode.getnamed("EME", "cells")),
           float(mode.getnamed("EME", "x")) * 1e6, L_TOT * 1e6))
    # Ports: NONE added. In MODE EME the two port planes are the ends of the EME span itself.
    # 2026-10-07: 12 candidate names for the added addemeport objects were all unselectable, i.e.
    # they were never the ports the user S-matrix reports -- so adding them was a wrong model.
    log("ports: none added (the two ends of the EME span act as the port planes)")
    log("EME: %d modes per cell group; ports at x=0 and x=%.1f um"
        % (N_MODES, L_TOT * 1e6))
    log("geometry built: Si strip %d vertices (%.1f um total), EME + 2 ports"
        % (len(strip_vertices()), L_TOT * 1e6))
    return None, None


def try_resources(mode):
    """Try every plausible shape of the resource API and record what the engine accepts.

    The licence grants 4 HPC tasks plus the 4 included cores, while the solver asked for 8 and
    the checkout was denied (FlexNet -25,147). Asking for 1 process (threads only) should stay
    inside the included cores. Which call actually bites is recorded rather than assumed.
    """
    forms = [
        ("setresource(prop, value, solver='MODE')", lambda: mode.setresource("processes", 1, "MODE")),
        ("setresource(prop, value, solver='mode')", lambda: mode.setresource("processes", 1, "mode")),
        ("setresource(prop, value, solver='Lumerical')", lambda: mode.setresource("processes", 1, "Lumerical")),
        ("setresource(prop, value, solver='lumerical')", lambda: mode.setresource("processes", 1, "lumerical")),
        ("setresource(prop, value)", lambda: mode.setresource("processes", 1)),
        ("setresource(solver='MODE', prop, value)", lambda: mode.setresource("MODE", "processes", 1)),
        ("setresource(solver='mode', prop, value)", lambda: mode.setresource("mode", "processes", 1)),
        ("setresource(prop, value, solver='eme')", lambda: mode.setresource("processes", 1, "eme")),
        ("setresource(prop, value, solver='FDTD')", lambda: mode.setresource("processes", 1, "FDTD")),
        ("setresource(prop='threads', value=4, solver='MODE')", lambda: mode.setresource("threads", 4, "MODE")),
        ("setresource(prop='threads', value=4, solver='mode')", lambda: mode.setresource("threads", 4, "mode")),
    ]
    recs = []
    for label, call in forms:
        try:
            call()
            recs.append({"form": label, "result": "OK"})
        except Exception as exc:  # noqa: BLE001 - probing an API, every failure is data
            recs.append({"form": label, "result": "FAIL: " + str(exc).splitlines()[0][:90]})
    for label, key in (("getresource('processes','MODE')", "MODE"), ("getresource('processes','mode')", "mode")):
        try:
            recs.append({"form": label, "result": "OK: %s" % mode.getresource("processes", key)})
        except Exception as exc:  # noqa: BLE001
            recs.append({"form": label, "result": "FAIL: " + str(exc).splitlines()[0][:90]})
    for r in recs:
        log("resource try: %-52s %s" % (r["form"], r["result"]))
    return recs


def engine_log_tail(project_path: str, n: int = 20) -> str:
    """Read (never write) the engine log that belongs to this project."""
    stem = os.path.splitext(project_path)[0] + "_p0.log"
    if not os.path.isfile(stem):
        return "no engine log at " + os.path.basename(stem)
    with open(stem, encoding="utf-8", errors="replace") as fh:
        return "".join(fh.readlines()[-n:])


def probe_ports(mode):
    """Find the real, selectable names of the EME ports and read their geometry back.

    Written after the lesson of 2026-10-07: the handles returned by addemeport() carry a local
    name that is NOT selectable, so every earlier 'the port is placed' statement was unverified.
    select(...) failure is therefore data, not noise; the first name that selects gets read back.
    """
    rec = {"tried": [], "found": None}
    for cand in ("port_1", "port_2", "port_3", "port_4", "port", "EME port",
                 "EME::port_1", "EME::port_2", "EME::port_3", "EME::port_4",
                 "EME port 1", "EME port 2"):
        ok = True
        try:
            mode.eval('select("%s");' % cand)
            mode.get("x")
        except Exception as exc:  # noqa: BLE001 - probing names, a failure is the answer
            ok = False
            rec["tried"].append({cand: str(exc).splitlines()[0][:60]})
        if ok:
            try:
                rec["found"] = {"name": cand, "x_um": float(mode.get("x")) * 1e6,
                                "y span_um": float(mode.get("y span")) * 1e6,
                                "z span_um": float(mode.get("z span")) * 1e6}
            except Exception as exc:  # noqa: BLE001
                rec["found"] = {"name": cand, "read_failed": str(exc).splitlines()[0][:60]}
            log("port probe: selectable name = %s  -> %s" % (cand, rec["found"]))
            break
    if rec["found"] is None:
        log("port probe: NO port object could be selected by any tried name")
    return rec


def run_point(mode, cell_um: float) -> dict:
    """One cell length: set the cell group, save, run, propagate, read the |S|^2 matrix."""
    cells = int(round(L_TOT / (cell_um * 1e-6)))
    project = os.path.join(HERE, "min_sbend_eme_%gum.lms" % cell_um)
    mode.switchtolayout()
    mode.setnamed("EME", "number of cell groups", 1)
    mode.setnamed("EME", "group spans", np.array([[L_TOT]]))
    mode.setnamed("EME", "cells", np.array([[cells]]))
    mode.save(project)
    log("--- point cell=%.2f um (%d cells) ---" % (cell_um, cells))
    mode.select("EME")
    mode.run()
    rec = {"cell_um": cell_um, "cells": cells, "project": os.path.basename(project)}
    try:
        mode.emepropagate()
        rec["propagate_ok"] = True
    except Exception as exc:  # noqa: BLE001 - a refused propagation is a result, not a crash
        rec["propagate_ok"] = False
        rec["propagate_error"] = str(exc).splitlines()[0][:120]
        rec["engine_log_tail"] = engine_log_tail(project)
        log("propagate refused: %s" % rec["propagate_error"])
        return rec
    got = None
    tried = []
    for _prov, _name in (("EME", "user s matrix"), ("EME", "power normalized user s matrix"),
                         ("EME", "S"), ("EME::EME", "user s matrix"), ("EME::EME", "S"),
                         ("::model::EME::EME", "user s matrix"), ("EME", "s matrix")):
        try:
            got = mode.getresult(_prov, _name)
            tried.append("%s / %s -> OK" % (_prov, _name))
            rec["result_provider"] = _prov
            rec["result_name"] = _name
            break
        except Exception as exc:  # noqa: BLE001
            tried.append("%s / %s -> FAIL" % (_prov, _name))
    rec["result_tries"] = tried
    try:
        keys = list(got.keys()) if hasattr(got, "keys") else None
        rec["result_keys"] = keys
        arr = None
        if keys and "S" in keys:
            arr = np.array(got["S"])
        elif hasattr(got, "shape"):
            arr = np.array(got)
        if arr is not None:
            a2 = np.abs(arr) ** 2
            rec["S_shape"] = list(a2.shape)
            rec["S_abs2"] = np.round(a2, 6).tolist()
            # both candidate metrics recorded raw; which element is which mode is read off the port
            # configuration, never assumed
            rec["colsum_per_input"] = np.round(a2.sum(axis=0), 6).tolist()
            rec["diag"] = np.round(np.diag(a2), 6).tolist()
            log("S shape=%s diag=%s colsum=%s" % (rec["S_shape"], rec["diag"], rec["colsum_per_input"]))
    except Exception as exc:  # noqa: BLE001
        rec["getresult_error"] = str(exc).splitlines()[0][:120]
        log("getresult refused: %s" % rec["getresult_error"])
    return rec


def main() -> int:
    ap = argparse.ArgumentParser(description="minimal S-bend in MODE EME: cell-length sweep")
    ap.add_argument("--cell-um", type=float, default=None,
                    help="a single cell length in um (default: 5, 2.5, 1)")
    args, _unknown = ap.parse_known_args()
    cell_list = [args.cell_um] if args.cell_um else [5.0, 2.5, 1.0]

    # Preferred: reuse a session that already lives in the caller's Lumerical environment (a plain
    # python process cannot load the interop DLL: WinError 14001, side-by-side configuration).
    mode = globals().get("_REUSE_HANDLE")
    if mode is None:
        try:
            import lumapi  # standalone: owns its own MODE session
        except ImportError:  # some installs only expose it under the ansys namespace
            from ansys.api.lumerical import lumapi  # noqa: F401
        log("opening MODE session")
        mode = lumapi.MODE(hide=False)
    else:
        log("reusing an existing MODE session handle")
    results = {
        "structure": {"L_tot_um": L_TOT * 1e6, "straight_um": L_STRAIGHT * 1e6,
                      "bend_um": L_BEND * 1e6, "dy_um": DY * 1e6, "w_um": W * 1e6,
                      "t_si_um": T_SI * 1e6, "lam_um": LAM * 1e6, "modes_per_port": N_MODES,
                      "materials": "Lumerical built-in Palik Si / SiO2 (declared substitution)"},
        "points": []}
    build_geometry(mode)
    results["port_probe"] = probe_ports(mode)
    results["resource_attempts"] = try_resources(mode)
    for c in cell_list:
        results["points"].append(run_point(mode, c))
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)
    with open(os.path.join(HERE, "results.csv"), "w", encoding="utf-8") as fh:
        fh.write("cell_um,cells,propagate_ok,colsum_per_input,diag\n")
        for p in results["points"]:
            fh.write("%s,%s,%s,%s,%s\n" % (p.get("cell_um"), p.get("cells"), p.get("propagate_ok"),
                                            p.get("colsum_per_input"), p.get("diag")))
    log("wrote results.json / results.csv in " + HERE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


