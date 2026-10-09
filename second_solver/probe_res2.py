# -*- coding: utf-8 -*-
"""probe_res2.py — try to lower the HPC task count with a solver object present + introspect."""
from __future__ import annotations


def attempt(handle, tag: str) -> dict:
    rec = {}
    handle.switchtolayout()
    handle.deleteall()
    try:
        handle.addfdtd()
        rec["addfdtd"] = "OK"
    except Exception as exc:  # noqa: BLE001
        rec["addfdtd"] = "FAIL:" + str(exc).splitlines()[0][:40]
    for label, fn in (
        ("set('processes',4,'FDTD')", lambda: handle.setresource("processes", 4, "FDTD")),
        ("set('processes',1,'FDTD')", lambda: handle.setresource("processes", 1, "FDTD")),
        ("set('threads',4,'FDTD')", lambda: handle.setresource("threads", 4, "FDTD")),
        ("get('processes','FDTD')", lambda: handle.getresource("processes", "FDTD")),
        ("set('processes',4,'fdtd')", lambda: handle.setresource("processes", 4, "fdtd")),
        ("set('processes',4,'FDTD Engine')", lambda: handle.setresource("processes", 4, "FDTD Engine")),
    ):
        try:
            v = fn()
            rec["%s|%s" % (tag, label)] = "OK:%s" % (str(v)[:20],)
        except Exception as exc:  # noqa: BLE001
            rec["%s|%s" % (tag, label)] = "FAIL:" + str(exc).splitlines()[0][:40]
    for code in ("setresource('processes',4,'FDTD');", "?setresource;", "?getresource;"):
        try:
            handle.eval(code)
            rec["%s|eval:%s" % (tag, code)] = "OK"
        except Exception as exc:  # noqa: BLE001
            rec["%s|eval:%s" % (tag, code)] = "FAIL:" + str(exc).splitlines()[0][:40]
    return rec
