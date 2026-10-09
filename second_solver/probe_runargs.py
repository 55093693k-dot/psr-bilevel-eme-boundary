# -*- coding: utf-8 -*-
"""probe_runargs.py — try run() resource arguments to avoid the 8-task HPC checkout.

The varFDTD run aborted with "only 4 of the requested 8 tasks were available (anshpc, -25,147)".
The documented run() positional args are (solver, resource_type, resource_name, cuda); this tries
a few resource-type overrides on the already-built varFDTD project.
"""
from __future__ import annotations

import numpy as np


def run(mode) -> dict:
    rec = {}
    mode.switchtolayout()
    for args in (("varFDTD", "CPU"), ("FDTD", "CPU"), ("varFDTD",), ()):
        try:
            mode.run(*args)
            rec["ran_with"] = list(args)
            break
        except Exception as exc:  # noqa: BLE001
            rec["run%s" % (list(args),)] = str(exc).splitlines()[0][:60]
    if "ran_with" in rec:
        for mname in ("monitor", "power"):
            try:
                T = np.real(np.array(mode.getresult(mname, "T")).ravel())
                rec["T"] = float(np.mean(T))
                break
            except Exception as exc:  # noqa: BLE001
                rec["T@" + mname] = str(exc).splitlines()[0][:40]
    return rec
