# -*- coding: utf-8 -*-
"""probe_res.py — can the HPC task count be set from script for the FDTD/varFDTD engine?

The varFDTD run aborted: "only 4 of the requested 8 tasks were available ... anshpc ... -25,147"
(same licence limit noted 2026-10-07 for the EME engine). If the request can be lowered from
script, the FDTD route opens; otherwise it is GUI-only (a user action).
"""
from __future__ import annotations


def probe(handle, tag: str) -> dict:
    rec = {"%s|resource_methods" % tag: [m for m in dir(handle) if "resource" in m.lower()]}
    for label, fn in (
        ("setresource processes=1 FDTD", lambda: handle.setresource("processes", 1, "FDTD")),
        ("setresource processes=1", lambda: handle.setresource("processes", 1)),
        ("setresource processes=4 FDTD", lambda: handle.setresource("processes", 4, "FDTD")),
        ("setresource threads=1 FDTD", lambda: handle.setresource("threads", 1, "FDTD")),
    ):
        try:
            fn()
            rec["%s|%s" % (tag, label)] = "OK"
        except Exception as exc:  # noqa: BLE001
            rec["%s|%s" % (tag, label)] = "FAIL:" + str(exc).splitlines()[0][:40]
    for obj in ("varFDTD", "FDTD"):
        for prop in ("processes", "threads", "number of processes", "number of threads"):
            try:
                rec["%s|%s" % (obj, prop)] = str(handle.getnamed(obj, prop))
            except Exception:  # noqa: BLE001
                rec["%s|%s" % (obj, prop)] = "FAIL"
    return rec
